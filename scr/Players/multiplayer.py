import time
import copy
import chess
from threading import Lock

from .user import User
from Networking.bits import Bits
from Networking.compression import compress_move, decompress_move
from Networking.compression import compress_fen, decompress_fen
from Networking.connector import Connector, Event
import widgets


class Multiplayer(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.debug:
            self.logger = widgets.Logger()
            self.logger.blacklist("heartbeat")

        if self.colour:
            ip = None
        else:
            window = widgets.Question()
            window.ask_for_ip()
            ip = window.wait()
            window.destroy()

        self.build_connection(ip, self.colour)
        self.event_lock = Lock()
        self.event_queue = []
        self.last_self_heartbeat = int(time.time())
        self.last_other_heartbeat = int(time.time())
        self._update()

    def push(self, move: chess.Move) -> None:
        """
        Tell GUIBoard about the new move
        """
        self.send_move(move)
        self.callback(move)

    def build_connection(self, ip: int, colour: bool) -> None:
        """
        This tries to build a connection. When successful
        `connector.connected` will be `True`
        """
        self.connector = Connector(ip=ip, port=65360, server=colour)
        self.connector.bind(self.receiver)
        if self.debug:
            self.logger.log("connection.build", ip, 65360, sep="  ")

    def send_move(self, move: chess.Move) -> None:
        """
        This function only encodes and sends a given move.
        """
        if self.connector.connected:
            if self.debug:
                self.logger.log("connection.send.move", str(move))
            compressed = compress_move(move).to_bytes()
            self.connector.send_data(compressed)

    def receiver(self, event: Event) -> None:
        """
        This adds the event to the event queue to be handled by _update.
        The event can't be handled here as tkinter will complain about
        the thread not being in the main loop.
        """
        self.event_lock.acquire()
        self.event_queue.append(event)
        self.event_lock.release()

    def _update(self) -> None:
        """
        A never ending loop of dealing with the event queue.
        Note: this loop stays in the main thread (the one tkinter needs)
        because it uses the tkinter `widget.after` method. This heavily
        relies on that so if it is changed it can cause massive problems.
        """
        self.event_lock.acquire()
        # We need to first deep copy the list so that we avoid any problems
        # accessing the data later.
        event_queue = copy.deepcopy(self.event_queue)
        self.event_queue = []
        self.event_lock.release()
        self.check_alive()
        # widget.after must be before the for loops as some events might
        # take over the thread.
        self.master.after(50, self._update)
        for event in event_queue:
            bits = event.data
            if len(bits) == 0:
                # Socket telling us that the connection is broken.
                if self.debug:
                    self.logger.log("connection.broken")
                    # Now we have to destroy this so we don't try to
                    # send any more moves.
                    self.destroy()
            elif len(bits) == 8:
                # We recved a heartbeat from the other player
                self.recieved_heartbeat(bits)
            elif len(bits) == 16:
                # We recved a move from the other player
                self.recieved_move(event)
            else:
                # We recved other larger data from the other player
                # Can be used for a simple chat plugin later
                self.revieved_large_data(bits)

    def check_alive(self) -> None:
        """
        Checks how long ago we send a heartbeat and sends one.
        """
        if time.time()-self.last_self_heartbeat > 0.5:
            self.send_heartbeat()
            self.last_self_heartbeat = time.time()

    def recieved_heartbeat(self, bits) -> None:
        """
        We recved a heartbeat so the other player hasn't died.
        Improvement: decode the data into something more usefull
        """
        if self.debug:
            self.logger.log("connection.recv.heartbeat")
        diff = self.last_other_heartbeat-time.time()
        if diff >= 5:
            print("other has bad connection")
        self.last_other_heartbeat = time.time()

    def send_heartbeat(self) -> None:
        """
        We need to send a heartbeat to show that we are alive.
        Improvement: change it so that we aren't just sending 0000 0000
        """
        if self.connector.connected:
            data = Bits.from_int(0, bits=8)
            self.connector.send_data(data.to_bytes(errors=None))
            if self.debug:
                self.logger.log("connection.send.heartbeat")

    def recieved_move(self, bits: Bits) -> None:
        """
        We need to decode the move and show it to the user
        """
        # Decoding the move
        move = decompress_move(bits.data)
        if move == None: # Check if it is corrupt
            if self.debug:
                self.logger.log("connection.recv.garbage")
            return None
        if move.from_square == move.to_square:
            # A special move
            self.special_move(move)
            return None
        # If the move is valid we need to make sure the promotion value
        # is also valid.
        if move not in self.board.legal_moves:
            move.promotion = None
        if self.debug:
            self.logger.log("connection.recv.move", move)
        # We need to tell GUIBoard that we recved a move.
        super().push(move)

    def revieved_large_data(self, bits: Bits) -> None:
        """
        This is called when we recv data that is larger than 2 bytes.
        It can be used for a simple chat plugin later.
        """
        if self.debug:
            self.logger.log("connection.recv.large_packet", len(bits), bits)
        print(repr(bits))

    def destroy(self) -> None:
        """
        This destroys the connection, closes the port and unbinds the socket.
        """
        self.connector.unbind()
        self.connector.kill()
        super().destroy()

    def special_move(self, move: chess.Move) -> None:
        """
        This deals with all of the special moves that are outlined in
        `Networking/compression.py`
        """
        code = move.from_square
        if code == 0:
            # other user requested undo
            self.undo()
        elif code == 1:
            # we requested undo and they rejected
            widgets.info("The other player declined your undo request.")
        elif code == 2:
            # we requested undo and they accepted
            self.request_undo()
        else:
            print("Illigal code: "+str(code))

    def send_special_move(self, code: int) -> None:
        """
        This sends a special move to the other player. Those moves
        are accually illegal but they encode for something.
        """
        self.send_move(chess.Move(from_square=code, to_square=code))

    def send_undo_move(self, _) -> None:
        self.send_special_move(code=0)

    def undo(self) -> str:
        """
        This is called when the other player want to undo and we
        can eather allow them or block them.
        """
        # Ask the user if they want to allow or block the undo request
        window = widgets.Question()
        window.ask_user_multichoice("The other player requested a move back.",
                                    ("Accept", "Decline"), (True, False))
        allowed = window.wait()
        window.destroy()
        if allowed:
            # Send confermation that we allowed it
            self.send_special_move(code=2)
            self.request_undo()
        else:
            # Send confermation that we blocked it
            self.send_special_move(code=1)

    def redo_move(self, move: chess.Move) -> str:
        """
        There is no point in redoing moves.
        """
        return "break"
