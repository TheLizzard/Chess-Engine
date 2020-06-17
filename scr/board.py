from io import StringIO
from chess import pgn
import tkinter as tk
import chess
import time
import re

from Players.user import User
from Players.computer import Computer
from Players.multiplayer import Multiplayer
from Players.test import Test

from piece import Piece
from position import Position
from Networking.connector import get_ip
from settings import Settings
import widgets

SETTINGS = Settings()
BOARD_SETTINGS = SETTINGS.gameboard


class GUIBoard:
    LETTER_TO_NAME = {"p": "pawn",
                      "r": "rook",
                      "k": "king",
                      "q": "queen",
                      "n": "knight",
                      "b": "bishop"}
    def __init__(self, root: tk.Tk, kwargs: dict, move_callback):
        self.root = root
        self.kwargs = kwargs
        self.undo_stack = []
        self.players = [None, None]
        self.move_callback = move_callback
        self.size = BOARD_SETTINGS.size_of_squares
        self.set_up_board()

    def done_move(self, move: chess.Move) -> None:
        self.push(move)
        self.update_last_moved()
        self.update()
        self.players[1-self.board.turn].go()

    def play(self) -> None:
        if not self.board.is_game_over():
            self.player[1-self.board.turn].go()
            self.update()

    def set_up_board(self) -> None:
        """
        This sets up the board by displaying all of the squares. It
        also starts 2 user players.
        """
        # Load the colours to show the user the last move that was played
        # and the colours for the black and white squares on the board
        self.last_move_colours = (BOARD_SETTINGS.last_move_colour_white,
                                  BOARD_SETTINGS.last_move_colour_black)
        self.white_sqrs = BOARD_SETTINGS.light_squares
        self.black_sqrs = BOARD_SETTINGS.dark_squares
        # Get a new chess Board and create a tkinter canvas
        self.board = chess.Board()
        self.master = tk.Canvas(self.root, width=self.size*8,
                                height=self.size*8, **self.kwargs)
        self.master.grid(row=1, column=1, rowspan=3)
        # This accualy sets up the squares
        self.create_board()

        # Start 2 user players playing as white and black
        self.add_user_as_player(True)
        self.add_user_as_player(False)
        self.players[0].go()

    def create_board(self) -> None:
        """
        This sets up the board by displaying all of the squares.
        """
        fill_white = False
        size = self.size
        # For each of the squares on the board
        for x in range(size, size*8+1, size):
            for y in range(size, size*8+1, size):
                # calculate the correct fill
                fill_white = not fill_white
                if fill_white:
                    fill = self.white_sqrs
                else:
                    fill = self.black_sqrs
                # fill in the square
                self.master.create_rectangle((x-size, y-size, x, y),
                                             fill=fill, width=0)
            fill_white = not fill_white
        self.set_up_pieces() # Set up the pieces

    def push(self, move: chess.Move) -> None:
        """
        Pushes the move and tells the parent about it.
        """
        # Reset the undo_stack
        self.undo_stack = []
        self.board.push(move)
        self.move_callback()

    def set_up_pieces(self) -> None:
        """
        Sets up the pieces by resetting `self.last_move_sqrs` and `self.pieces`
        """
        self.last_move_sqrs = [None, None]
        self.pieces = []
        self.update()

    def update(self, redraw=True) -> None:
        """
        This redraws the pieces on the board if `redraw` is True
        Else just updates the root.
        """
        if redraw:
            # Remove all of the pieces' sprites
            self.delete_sprites()
            # For each square on the board
            for i in range(64):
                position = Position.from_int(i)
                # Check what piece must be there and create it
                piece = self.position_to_piece(position, create=True)
                if piece is not None:
                    self.pieces.append(piece) # Add it to self.pieces
                    piece.show() # Show it to the screen
        self.root.update()

    def create_piece(self, **kwargs) -> Piece:
        """
        Creates a new piece and resizes it
        """
        new_piece = Piece(master=self.master, **kwargs)
        new_piece.resize_scale(scale=BOARD_SETTINGS.scale_for_pieces)
        return new_piece

    def delete_sprites(self) -> None:
        """
        Delete all of the pieces' sprites
        """
        for pieces in self.pieces:
            pieces.destroy()
        self.pieces.clear() # Can't use `self.pieces = []`

    def position_to_piece(self, position: Position, create=False) -> Piece:
        """
        This returns the piece from a given square by eather:
            creating a new piece (if create is True) or
            find the piece in `self.pieces` (if create is False)
        """
        if create:
            # Find the correct piece type and colour
            piece = self.board.piece_at(position.to_int())
            if piece is None:
                return None
            name = self.LETTER_TO_NAME[piece.symbol().lower()]
            # Create the new piece
            piece = self.create_piece(name=name, colour=piece.color,
                                      position=position)
            return piece
        else:
            # Find the piece with the matching position and return it
            # This may return None if the piece is not found
            for piece in self.pieces:
                if piece.position == position:
                    return piece

    def fen(self) -> str:
        """
        Returns the fen string of the current board position
        """
        return self.board.fen()

    def pgn(self) -> str: # chess.Board is missing .pgn()
        """
        Returns the PGN current board state in sans notation.
        """
        board = chess.Board()
        pgn = board.variation_san(self.board.move_stack)
        pgn = self.clean_pgn(pgn)
        return pgn

    def clean_pgn(self, pgn: str) -> str:
        """
        This cleans the fen string from "1. e4 e5 2. d4 exd4" to
        "1. e4 e5\n2. d4 exd4"
        """
        pgn = re.split("\d+\. ", pgn)[1:]
        output = ""
        for i, move_pair in enumerate(pgn):
            output += str(i+1)+". "+move_pair.rstrip()+"\n"
        return output

    def set_pgn(self, pgn: str) -> None:
        """
        Sets up the board accourding to the pgn if allowed by both current
        players.
        """
        for player in self.players:
            if player.open_game(pgn) == "break":
                return "break"
        self.reset()
        game = chess.pgn.read_game(StringIO(pgn))
        for move in game.mainline_moves():
            self.board.push(move)
        self.update()

    # This is the part where the players are accually created and added to
    # the board using the board player protocol

    def add_user_as_player(self, colour: bool) -> None:
        """
        This adds an user as the player.
        """
        self.kill_player(colour)
        player = User(self.board, self.master, colour, self.pieces,
                      self.update, self.done_move, self.request_undo_move,
                      self.request_redo_move)
        self.add_player(colour, player)

    def add_computer_as_player(self, colour: bool) -> None:
        """
        This adds a computer as the player. The computer is played by
        Stockfish.
        """
        self.kill_player(colour)
        player = Computer(self.board, self.master, colour, self.pieces,
                          self.update, self.done_move, self.request_undo_move,
                          self.request_redo_move)
        self.add_player(colour, player)

    def add_ai_as_player(self, colour: bool) -> None:
        """
        This adds an ai as the player.
        """
        if type(colour) != bool:raise
        print("Not available")

    def start_multiplayer(self) -> None:
        """
        This adds 2 players which are the same object in memory.
        There is not difference between being the server and the client.
        They both do the same but the server always plays as white.
        """
        # This shows the user's IP and asks if the user wants to play as
        # black or white
        ip_text = "Your IP is: "+get_ip()
        colour = self.ask_user(ip_text+"\nDo you want to play as white?",
                               ("yes", "no"), (True, False))
        if colour is None:
            return None
        self.kill_player(colour)
        self.kill_player(not colour)
        player = Multiplayer(self.board, self.master, colour, self.pieces,
                             self.update, self.done_move,
                             self.request_undo_move, self.request_redo_move,
                             debug=True)
        self.add_player(colour, player)
        # This is only for testing purposess.
        """
        player = Test(self.board, self.master, not colour, self.pieces,
                      self.update, self.done_move, self.request_undo_move,
                      self.request_redo_move, debug=True)
        """
        self.add_player(not colour, player)

    def kill_player(self, colour: bool) -> None:
        """
        If there is already a player taking the board we need to delete it.
        Fix for Issue #10 and partial fix for Issue #13
        """
        if self.players[not colour] is not None:
            self.players[not colour].destroy()
            old_player = self.players[not colour]
            del old_player

    def add_player(self, colour: bool, player) -> None:
        """
        This adds the player to `self.players`.
        """
        player.start() # We need to start the player.
        self.players[not colour] = player

    def reset(self) -> None:
        """
        Reset the board by clearing the board and addeing new pieces.
        """
        self.remove_last_sqrs()
        self.board.reset()
        self.update()
        self.players[0].go()

    def moves_to_san(self, moves: list) -> list:
        """
        It changes a list of `chess.Move`s to a list of str containg
        the sans representation of the moves.
        Note: be careful as the moves are board dependant!
        With a different board you might get a lot of errors. Call this
        inside a `try` `except` block.
        """
        # create a deepcopy of the board so that we don't effect the real one
        board = self.board.copy()
        output = []
        # for each one of the moves push the move and add the sans
        # representation of it to the output
        for move in moves:
            output.append(board.san(move))
            board.push(move)
        return output

    def update_last_moved(self) -> None:
        """
        Update the sprites that show the last played move. This is done by
        using the `peek` method of `chess.Board` to see the last move.
        """
        self.remove_last_sqrs()
        # We need to check if any moves have been played
        if len(self.board.move_stack) > 0:
            move = self.board.peek()
            _from = Position.from_int(move.from_square)
            _to = Position.from_int(move.to_square)
            self.last_move_sqrs[0] = self.colour_sqr(_from)
            self.last_move_sqrs[1] = self.colour_sqr(_to)

    def remove_last_sqrs(self) -> None:
        """
        Removes the sprites showing the last played move.
        """
        if self.last_move_sqrs[0] is not None:
            self.master.delete(self.last_move_sqrs[0])
            self.master.delete(self.last_move_sqrs[1])

    def colour_sqr(self, position: Position) -> int:
        """
        Colours in a square.
        """
        colour = position.to_colour()
        colour = self.last_move_colours[colour]
        coords = position.to_coords_start()+position.to_coords_end()
        rectangle = self.master.create_rectangle(coords, fill=colour, width=0)
        return rectangle

    def request_undo_move(self) -> str:
        """
        This is called when a player requests an undo of a move.
        This is in the board player protocol.
        """
        if len(self.board.move_stack) == 0:
            return "break"
        move = self.board.peek()
        for player in self.players:
            result = player.undo_move(move)
            if result == "break":
                # If "break" of the current players rejected the undo
                return "break"
        self.board.pop()
        self.undo_stack.append(move)
        self.update_last_moved()
        self.update()
        self.move_callback()

    def request_redo_move(self):
        """
        This is called when a player requests a redo of a move.
        This is in the board player protocol.
        """
        if len(self.undo_stack) == 0:
            return "break"
        move = self.undo_stack[-1]
        for player in self.players:
            result = player.redo_move(move)
            if result == "break":
                # If "break" of the current players rejected the redo
                return "break"
        self.undo_stack.pop()
        self.board.push(move)
        self.update_last_moved()
        self.update()
        self.move_callback()

    def start_player(self) -> None:
        """
        Starts the player that is supposed to be playing on
        the board with now
        """
        self.players[1-self.board.turn].go()

    def ask_user(self, question: str, answers: tuple, mapping: tuple=None):
        """
        Asks the user a question in a new tkinter window using the
        `widgets.py` library
        """
        x, y = self.root.winfo_x(), self.root.winfo_y()
        window = widgets.Question(x, y)
        window.ask_user_multichoice(question, answers, mapping)
        result = window.wait()
        return result
