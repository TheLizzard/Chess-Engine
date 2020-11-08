from copy import deepcopy
from time import sleep
import subprocess
import os

import chess.polyglot
import chess.syzygy
import chess


import Constants.settings as settings
from .player import Player


AI_FOLDER = settings.Settings().evaluation.ai.replace("/", "\\")
os_bits = str(settings.get_os_bits()) # Get the bit version of the OS
os_extension = settings.get_os_extension()
RUN_COMMAND = os.getcwd()+"\\"+AI_FOLDER+os_bits+"bit"+os_extension
del AI_FOLDER, os_bits, os_extension # clean up


class AI(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def go(self) -> None:
        if self.board.turn != self.colour:
            return None
        if self.alowed_to_play:
            move = self.check_tables(self.board)
            if move is not None:
                self.callback(move)
                return None
            number_of_moves_played = len(self.board.move_stack)

            number_of_pieces = self.number_of_pieces(self.board.board_fen())

            if number_of_pieces < 10:
                depth = 5
                quietness = 4
            elif number_of_pieces < 21:
                depth = 4
                quietness = 3
            else:
                depth = 3
                quietness = 3

            folder = os.getcwd()+"\\ccarotmodule\\"
            hashed_move = str(self._go(folder, self.board,
                                       str(depth), str(quietness)))
            move = self.decode_move(hashed_move)
            self.callback(move)

    def decode_move(self, hashed_move):
        while len(hashed_move) < 5:
            hashed_move = "0"+hashed_move
        _from = int(hashed_move[:2])
        to = int(hashed_move[2:4])
        promotion = int(hashed_move[4])+1
        move = chess.Move(_from, to, promotion)
        if move not in self.board.legal_moves:
            move = chess.Move(_from, to)
        return move
    
    def number_of_pieces(self, fen):
        fen = fen.lower()
        number = 0
        for piece_type in ("p", "k", "b", "r", "q"):
            number += fen.count(piece_type)
        return number+2 # Add 2 for the 2 kings

    def check_tables(self, board):
        move = self.polyglot_move(board)
        if move is None:
            return self.syzygy_move(board)
        else:
            return move

    def polyglot_move(self, board):
        polyglot_folder = "Tables/polyglot.bin"
        with chess.polyglot.open_reader(polyglot_folder) as polyglot:
            move = polyglot.get(board)
            if move is not None:
                move = move.move
        return move

    def syzygy_move(self, board):
        value = self.syzygy(board)
        if value is None:
            return None
        sign = int(value/abs(value))
        for move in board.legal_moves:
            child = deepcopy(board)
            child.push(move)
            new_value = self.syzygy(child)
            if new_value == 0:
                continue
            if -sign == int(new_value/abs(new_value)):
                if abs(new_value) == abs(value)-1:
                    return move

    def syzygy(self, board):
        syzygy_folder = "Tables/syzygy/"
        with chess.syzygy.open_tablebase(syzygy_folder) as syzygy:
            move = syzygy.get_dtz(board)
        return move

    def _go(self, folder, board, depth, quietness) -> int:
        command = [RUN_COMMAND, folder, board.fen(), depth, quietness]
        print(command)
        process = subprocess.Popen(command, shell=True)
        while process.poll() is None:
            sleep(0.5)
        _eval = process.returncode
        return _eval

    def open_game(self, pgn: str) -> str:
        return "break"

    def set_fen(self, fen: str) -> str:
        return "break"
