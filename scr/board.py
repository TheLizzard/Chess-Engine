import tkinter as tk
import widgets
import chess
import time
import re

from piece import Piece
from position import Position
from Players.user import User
from Players.computer import Computer
from Players.multiplayer import Multiplayer
from Players.test import Test

from Networking.connector import get_ip


class GUIBoard:
    LETTER_TO_NAME = {"p": "pawn",
                      "r": "rook",
                      "k": "king",
                      "q": "queen",
                      "n": "knight",
                      "b": "bishop"}
    def __init__(self, settings, root, kwargs, undo, move_callback=None):
        self.root = root
        self.kwargs = kwargs
        self.allowed_undo = undo
        self.settings = settings
        self.players = [None, None]
        self.move_callback = move_callback
        self.size = self.settings.size_of_squares
        self.set_up_board()

    def sleep(self):
        self.add_user_as_player("black")
        self.add_user_as_player("white")
        self.players[0].go()

    def done_move(self, move):
        self.push(move)
        self.update()
        self.players[1-self.board.turn].go()

    def play(self):
        if not self.board.is_game_over():
            self.player[1-self.board.turn].go()
            self.update()

    def set_up_board(self):
        self.last_move_colours = (self.settings.last_move_colour_white,
                                  self.settings.last_move_colour_black)
        self.board = chess.Board()
        self.master = tk.Canvas(self.root, width=self.size*8,
                                height=self.size*8, **self.kwargs)
        self.master.grid(row=1, column=1, rowspan=3)
        self.white_sqrs = self.settings.light_squares
        self.black_sqrs = self.settings.dark_squares
        self.create_board()
        self.sleep()

    def add_user_as_player(self, colour):
        colour = self.colour_to_bool(colour)
        player = User(guiboard=self, board=self.board, master=self.master,
                      colour=colour, callback=self.done_move)
        self.add_player(colour, player)

    def add_computer_as_player(self, colour):
        colour = self.colour_to_bool(colour)
        player = Computer(board=self.board, colour=colour,
                          callback=self.done_move)
        self.add_player(colour, player)

    def add_player(self, colour, player):
        if self.players[1-colour] is not None:
            self.players[1-colour].destroy()
            p = self.players[1-colour]
            del p
        player.start()
        self.players[1-colour] = player

    def add_ai_as_player(self, colour):
        print("Not available")

    def start_multiplayer(self):
        ip_text = "Your IP is: "+get_ip()
        colour = self.ask_user(ip_text+"\nDo you want to be the server?",
                               ("y", "n"), (True, False))
        if not colour:
            window = widgets.Question()
            window.ask_for_ip()
            window.wait()
            ip = window.result
            window.destroy()
        else:
            ip = None
        player = Multiplayer(ip=ip, guiboard=self, board=self.board,
                             master=self.master, colour=colour,
                             callback=self.done_move)
        self.add_player(colour, player)
        #player = Test(ip="127.0.0.1", master=self.master, board=self.board,
        #              colour=1-colour, callback=self.done_move)
        self.add_player(1-colour, player)

    def ask_user(self, question, answers, mapping=None):
        window = widgets.Question()
        window.ask_user_multichoice(question, answers, mapping)
        window.wait()
        result = window.result
        window.destroy()
        return result

    def push(self, move):
        self.board.push(move)
        if self.move_callback is not None:
            self.move_callback()

    def colour_sqr(self, position):
        colour = position.to_colour()
        colour = self.last_move_colours[colour]
        coords = position.to_coords_start()+position.to_coords_end()
        rectangle = self.master.create_rectangle(coords, fill=colour, width=0)
        return rectangle

    def set_up_pieces(self):
        self.last_move_sqrs = [None, None]
        self.pieces = []
        self.update()

    def update(self, **kwargs):
        self.delete_sprites()
        self.update_last_moved()
        for x in range(1, 9):
            for y in range(1, 9):
                position = Position(x, y)
                piece = self.position_to_piece(position, create=True)
                if piece is not None:
                    self.pieces.append(piece)
                    piece.show()
        self.root.update()

    def create_piece(self, **kwargs):
        kwargs.update({"settings": self.settings})
        kwargs.update({"master": self.master})
        new_piece = Piece(**kwargs)
        new_piece.resize_scale(scale=self.settings.scale_for_pieces)
        return new_piece

    def create_board(self):
        fill_white = False
        size = self.size
        for x in range(size, size*8+1, size):
            for y in range(size, size*8+1, size):
                fill_white = not fill_white
                if fill_white:
                    fill = self.white_sqrs
                else:
                    fill = self.black_sqrs
                self.master.create_rectangle((x-size, y-size, x, y),
                                             fill=fill, width=0)
            fill_white = not fill_white
        self.set_up_pieces()

    def delete_sprites(self):
        for sprite in self.pieces:
            sprite.destroy()
        self.pieces = []

    def position_to_piece(self, position, board=None, create=False):
        if create:
            piece = self.board.piece_at(position.to_int())
            if piece is None:
                return None
            colour = "white" if piece.color else "black"
            letter = piece.symbol().lower()
            name = self.LETTER_TO_NAME[letter]
            piece = self.create_piece(name=name, colour=colour, position=position)
            return piece
        else:
            for piece in self.pieces:
                if piece.position == position:
                    return piece

    def colour_to_bool(self, colour):
        if isinstance(colour, str):
            if colour == "white":
                return True
            elif colour == "black":
                return False
        elif isinstance(colour, bool):
            return colour
        elif isinstance(colour, int) and ((0 == colour) or (1 == colour)):
            return colour

    def fen(self):
        return self.board.fen()

    def pgn(self): # chess.Board is missing .pgn()
        board = chess.Board()
        pgn = board.variation_san(self.board.move_stack)
        pgn = self.clean_pgn(pgn)
        return pgn

    def clean_pgn(self, pgn):
        pgn = re.split("\d+\. ", pgn)[1:]
        output = ""
        for i, move_pair in enumerate(pgn):
            output += str(i+1)+". "+move_pair.rstrip()+"\n"
        return output

    def ask_if_user_white(self):
        self.players[0].stop();self.players[1].stop()
        colour = self.ask_user("Do you want to be black or white?",
                               ("w", "b"), (1, 0))
        self.players[0].start();self.players[1].start()
        return colour

    def start_ai_v_hum(self, colour):
        self.add_user_as_player(colour)
        self.add_ai_as_player(bool(1-colour))
        self.reset()

    def start_comp_v_hum(self, colour):
        self.add_user_as_player(colour)
        self.add_computer_as_player(bool(1-colour))
        self.reset()

    def start_hum_v_hum(self):
        self.add_user_as_player(True)
        self.add_user_as_player(False)
        self.reset()

    def reset(self):
        self.remove_last_sqrs()
        self.board.reset()
        self.update()
        self.players[0].go()

    def remove_last_sqrs(self):
        if self.last_move_sqrs[0] is not None:
            self.master.delete(self.last_move_sqrs[0])
            self.master.delete(self.last_move_sqrs[1])

    def moves_to_san(self, moves): # board dependant
        board = self.board.copy()
        output = []
        for move in moves:
            output.append(self.move_to_san(move, board))
            board.push(move)
        return output

    def move_to_san(self, move, board):
        return board.san(move)

    def update_last_moved(self):
        self.remove_last_sqrs()
        if len(self.board.move_stack) > 0:
            move = self.board.peek()
            _from = Position.from_int(move.from_square)
            _to = Position.from_int(move.to_square)
            self.last_move_sqrs[0] = self.colour_sqr(_from)
            self.last_move_sqrs[1] = self.colour_sqr(_to)

    def undo_move(self):
        if self.allowed_undo[1-self.board.turn]:
            move = self.board.pop()
            for player in self.players:
                player.undo_move(move)
            return move
        else:
            return "break"

    def redo_move(self, move):
        if self.allowed_undo[1-self.board.turn]:
            self.board.push(move)
            for player in self.players:
                player.redo_move(move)
        else:
            return "break"

    def start_player(self):
        self.players[1-self.board.turn].go()

    @property
    def double_undo_redo(self):
        return isinstance(self.players[1-self.board.turn], Computer)

    @property
    def move_stack(self):
        return self.board.move_stack
