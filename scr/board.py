from piece import Piece
import tkinter as tk
import chess
import time
import re

from user import User
from computer import Computer
from position import Position


class GUIBoard:
    LETTER_TO_NAME = {"p": "pawn",
                      "r": "rook",
                      "k": "king",
                      "q": "queen",
                      "n": "knight",
                      "b": "bishop"}
    def __init__(self, settings, root, kwargs):
        #              [white player, black player]
        self.players = [None, None]
        # has to be an object like: <Player> or <Computer> or <AI>
        self.settings = settings
        self.root = root
        self.kwargs = kwargs
        self.size = self.settings.size_of_squares
        self.set_up_board()

    def sleep(self):
        self.add_user_as_player("black")
        self.add_user_as_player("white")
        self.players[0].go()

    def done_move(self):
        self.update()
        self.players[1-self.board.turn].go()

    def play(self):
        if not self.board.is_game_over():
            self.player[1-self.board.turn].go()
            self.update()

    def set_up_board(self):
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

    def set_up_pieces(self):
        self.pieces = []
        self.update()

    def update(self, **kwargs):
        self.delete_sprites()
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

    def position_to_piece(self, position, create=False):
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
        pgn = re.split("\d\. ", pgn)[1:]
        output = ""
        for i, move_pair in enumerate(pgn):
            output += str(i+1)+". "+move_pair.rstrip()+"\n"
        return output

    def ask_if_user_white(self):
        self.colour_chosen = None
        coords = (3*self.size, 3*self.size, 5*self.size, 4*self.size)
        r = self.master.create_rectangle(*coords, fill="black")
        text = "White or black?\nClick on the square bellow"
        t = self.master.create_text(4*self.size, 3.5*self.size, fill="white",
                                    font=("", 5), text=text, justify="center")
        self.master.bind("<Button-1>", self.received_user_colour, True)
        self.players[0].stop();self.players[1].stop()
        while self.colour_chosen is None:
            self.root.update()
            time.sleep(0.01)
        self.players[0].start();self.players[1].start()
        self.master.delete(r)
        self.master.delete(t)
        return self.colour_chosen

    def received_user_colour(self, event):
        if 3*self.size <= event.x <= 5*self.size:
            if 4*self.size <= event.y <= 5*self.size:
                w = (event.x-3*self.size)//45 == 0
                self.colour_chosen = w

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
        self.board.reset()
        self.update()
        self.players[0].go()
