"""
This is a client for the multiplayer as it is har to run both the multiplayer
client and server on the same computer.
"""
import time
import copy
import chess
from threading import Lock

from .player import Player
from Networking.bits import Bits
from Networking.compression import compress_move, decompress_move
from Networking.compression import compress_fen, decompress_fen
from Networking.connector import Connector
import widgets


class Test(Player):
    def __init__(self, ip, master, board, colour, debug=False, callback=None):
        self.debug = debug
        if self.debug:
            self.logger = widgets.Logger()
            self.logger.blacklist("heartbeat")
        self.event_queue = []
        self.event_lock = Lock()
        self.master = master
        self.board = board
        self.colour = colour
        self.callback = callback
        self.build_connection(ip, colour)
        self.last_self_heartbeat = int(time.time())
        self.last_other_heartbeat = int(time.time())
        self.update()

    def push(self, move):
        if self.debug:
            self.logger.log("push.move", move)
        self.send_move(move)
        if self.callback is not None:
            self.callback()

    def build_connection(self, ip, colour):
        if self.debug:
            self.logger.log("connection.build", ip, 65360)
        self.connector = Connector(ip=ip, port=65360, server=colour)
        self.connector.bind(self.receiver)

    def send_move(self, move):
        if self.debug:
            self.logger.log("connection.send.move", move)
        compressed = compress_move(move).to_bytes()
        self.connector.send_data(compressed)

    def receiver(self, event):
        self.event_lock.acquire()
        self.event_queue.append(event)
        self.event_lock.release()

    def update(self):
        self.event_lock.acquire()
        event_queue = copy.deepcopy(self.event_queue)
        self.event_queue = []
        self.event_lock.release()
        self.check_alive()
        for event in event_queue:
            if len(event) == 0:
                if self.debug:
                    self.logger.log("connection.broken")
            if len(event) == 1:
                self.revieved_heartbeat(event)
            elif len(event) == 2:
                self.recieved_move(event)
            else:
                if self.debug:
                    self.logger.log("connection.recv.largepacket", event.data)
        self.master.after(100, self.update)

    def check_alive(self):
        if time.time()-self.last_self_heartbeat > 3:
            self.send_heartbeat()

    def send_heartbeat(self):
        self.last_self_heartbeat = int(time.time())
        data = Bits.from_int(self.last_self_heartbeat%256)
        if self.debug:
            self.logger.log("connection.send.heartbeat")
        self.connector.send_data(data.to_bytes(errors=None))
        self.last_self_heartbeat = int(time.time())

    def revieved_heartbeat(self, event):
        if self.debug:
            self.logger.log("connection.recv.heartbeat")
        diff = self.last_other_heartbeat-int(time.time())
        if diff >= 5:
            if self.debug:
                self.logger.log("connection.other", "is bad")
            print("other has bad connection")
        self.last_other_heartbeat = int(time.time())

    def recieved_move(self, event):
        move = decompress_move(event.data)
        if self.debug:
            self.logger.log("connection.recv.move", move)
        if move == "corrupted data":
            return None
        if move not in self.board.legal_moves:
            move.promotion = None

        print(self.board)
        move = chess.Move.from_uci(input("uci move: "))
        self.send_move(move)

        if self.callback is not None:
            self.callback()

    def go(self):
        pass
