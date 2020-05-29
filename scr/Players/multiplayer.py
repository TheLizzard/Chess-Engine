import time
import copy
from threading import Lock

from .user import User
from Networking.bits import Bits
from Networking.compression import compress_move, decompress_move
from Networking.compression import compress_fen, decompress_fen
from Networking.connector import Connector


class Multiplayer(User):
    def __init__(self, ip, guiboard, board, master, colour, callback=None):
        self.build_connection(ip, colour)
        self.event_lock = Lock()
        self.event_queue = []
        self.master = master
        self._update()
        super().__init__(guiboard=guiboard, board=board, master=master,
                         colour=colour, callback=None)

    def push(self, move):
        self.send_move(move)
        super().push(move)

    def build_connection(self, ip, colour):
        self.connector = Connector(ip=ip, port=65360, server=colour)
        self.connector.bind(self.receiver)

    def send_move(self, move):
        compressed = compress_move(move).to_bytes()
        self.connector.send_data(compressed)

    def receiver(self, event):
        self.event_lock.acquire()
        self.event_queue.append(event)
        self.event_lock.release()

    def _update(self):
        self.event_lock.acquire()
        event_queue = copy.deepcopy(self.event_queue)
        self.event_queue = []
        self.event_lock.release()
        self.master.after(500, self._update)
        for event in event_queue:
            if len(event) == 1:
                self.revieved_heartbeat(event)
            elif len(event) == 2:
                self.recieved_move(event)
            else:
                self.revieved_large_data(event)

    def revieved_heartbeat(self, event):
        self.last_other_heartbeat = int(time.time())
        diff = self.last_other_heartbeat-int(event.data)
        if diff >= 20:
            print("other has bad connection")

    def send_heartbeat(self):
        self.last_self_heartbeat = int(time.time())
        data = Bits.from_int(self.last_self_heartbeat%256)
        self.connector.send_data(data)

    def recieved_move(self, event):
        move = decompress_move(event.data)
        if move == "corrupted data":
            return None
        if move not in self.board.legal_moves:
            move.promotion = None
        super().push(move)

    def revieved_large_data(self, event):
        print(repr(event.data))
