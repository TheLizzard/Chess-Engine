import time
import copy
from threading import Lock

from .user import User
from Networking.bits import Bits
from Networking.compression import compress_move, decompress_move
from Networking.compression import compress_fen, decompress_fen
from Networking.connector import Connector
import widgets


class Multiplayer(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.debug:
            self.logger = widgets.Logger()
            #self.logger.blacklist("heartbeat")

        if self.colour:
            ip = None
        else:
            window = widgets.Question()
            window.ask_for_ip()
            window.wait()
            ip = window.result
            window.destroy()

        self.build_connection(ip, self.colour)
        self.event_lock = Lock()
        self.event_queue = []
        self.last_self_heartbeat = int(time.time())
        self.last_other_heartbeat = int(time.time())
        self._update()

    def push(self, move):
        self.send_move(move)
        self.callback(move)

    def build_connection(self, ip, colour):
        self.connector = Connector(ip=ip, port=65360, server=colour)
        self.connector.bind(self.receiver)
        if self.debug:
            self.logger.log("connection.build", ip, 65360, sep="  ")

    def send_move(self, move):
        if self.connector.connected:
            if self.debug:
                self.logger.log("connection.send.move", str(move))
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
        self.check_alive()
        self.master.after(50, self._update)
        for event in event_queue:
            if len(event) == 0:
                if self.debug:
                    self.logger.log("connection.broken")
            elif len(event) == 1:
                if self.debug:
                    self.logger.log("connection.recv.heartbeat")
                self.recieved_heartbeat(event)
            elif len(event) == 2:
                self.recieved_move(event)
            else:
                if self.debug:
                    self.logger.log("connection.recv.large_packet", event.data)
                self.revieved_large_data(event)

    def check_alive(self):
        if time.time()-self.last_self_heartbeat > 3:
            self.send_heartbeat()

    def recieved_heartbeat(self, event):
        diff = self.last_other_heartbeat-int(time.time())
        if diff >= 5:
            print("other has bad connection")
        self.last_other_heartbeat = int(time.time())

    def send_heartbeat(self):
        if self.connector.connected:
            self.last_self_heartbeat = int(time.time())
            data = Bits.from_int(self.last_self_heartbeat%256)
            self.connector.send_data(data.to_bytes(errors=None))
            self.last_self_heartbeat = int(time.time())
            if self.debug:
                self.logger.log("connection.send.heartbeat")

    def recieved_move(self, event):
        move = decompress_move(event.data)
        if move == "corrupted data":
            if self.debug:
                self.logger.log("connection.recv.move", move)
            return None
        if move not in self.board.legal_moves:
            move.promotion = None
        if self.debug:
            self.logger.log("connection.recv.move", move)
        super().push(move)

    def revieved_large_data(self, event):
        print(repr(event.data))

    def destroy(self):
        raise NotImplementedError("Still working on destroying the " \
                                  "connection safely")
        super().destroy()
