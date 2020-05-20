from piece import Piece
import tkinter as tk
import chess

from user import User
from computer import Computer


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
        self.add_user_as_player("black", control=False)
        self.add_user_as_player("white", control=False)

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

    def add_user_as_player(self, colour, control=True):
        colour = self.colour_to_bool(colour)
        player = User(guiboard=self, board=self.board, master=self.master,
                        colour=colour, control=control)
        player.start()
        if self.players[1-colour] is not None:
            self.players[1-colour].destroy()
            del self.players[1-colour]
        self.players[1-colour] = player

    def add_computer_as_player(self, colour):
        colour = self.colour_to_bool(colour)
        player = Computer(board=self.board, colour=colour)
        player.start()
        self.players[1-colour] = player

    def set_up_pieces(self):
        self.pieces = []
        self.update()

    def update(self, **kwargs):
        self.delete_sprites()
        for x in range(1, 9):
            for y in range(1, 9):
                position = (x, y)
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

    def position_to_int(self, position):
        x, y = position
        return 8*y+x-9

    def int_to_position(self, _int):
        x = _int%8+1
        y = _int//8+1
        return (x, y)

    def position_to_piece(self, position, create=False):
        if create:
            position_as_int = self.position_to_int(position)
            piece = self.board.piece_at(position_as_int)
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

    def position_to_coords(self, position):
        x, y = position
        y = 8-y
        return (int((x-0.5)*self.size+0.5), int((y+0.5)*self.size+0.5))

    def coords_to_position(self, coords):
        x, y = coords
        new_x = x//self.size+1
        new_y = (self.size*8-y)//self.size+1
        return (int(new_x+0.5), int(new_y+0.5))

    def position_to_place(self, position):
        x, y = position
        return chess.FILE_NAMES[x-1]+str(y)

    def positions_to_uci(self, position1, position2):
        place1 = self.position_to_place(position1)
        place2 = self.position_to_place(position2)
        return place1 + place2

    def colour_to_bool(self, colour):
        if isinstance(colour, str):
            if colour == "white":
                return True
            elif colour == "black":
                return False
        elif isinstance(colour, bool):
            return colour
