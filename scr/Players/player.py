"""
Defines the Player class that can be inherited from.
"""


import chess


class Player:
    def __init__(self, board, master, colour, pieces, update, callback,
                 request_undo, request_redo, debug=False):
        """
 -------------- -------------------- ---------------------------------------- 
| Variable     | Type               | Further info                           |
 -------------- -------------------- ---------------------------------------- 
| board        | chess.Board object | Never push moves, call self.callback   |
| master       | tk.Canvas object   |                                        |
| colour       | bool               | The colour of the player               |
| pieces       | [piece.Piece, ...] | The pieces on GUIBoard                 |
| debug        | bool               | Used only in testing                   |
| request_undo | function           | used to requst an undo                 |
| request_redo | function           | used to requst an redo                 |
| callback     | function           | use: `self.callback(move: chess.Move)` |
| update       | function           | use: `self.update(redraw: bool)`       |
 -------------- -------------------- ---------------------------------------- 
        """
        self.board = board
        self.master = master
        self.colour = colour
        self.pieces = pieces
        self.update = update
        self.callback = callback
        self.request_undo = request_undo
        self.request_redo = request_redo
        self.debug = debug

        self.alowed_to_play = False

    def start(self) -> None:
        self.alowed_to_play = True

    def stop(self) -> None:
        self.alowed_to_play = False

    def destroy(self) -> None:
        """
        After this method is called the player must stop immediately.
        """
        self.stop()

    def undo_move(self, move: chess.Move) -> str:
        """
        Called when the user wants to undo a move.
        If "break" is returned the undo will be blocked
        """
        pass

    def redo_move(self, move: chess.Move) -> str:
        """
        Called when the user wants to redo a move.
        If "break" is returned the redo will be blocked
        """
        pass

    def go(self) -> None:
        """
        Called every time the GUIBoard needs the player to move
        Always call with the move `self.callback(move)`
        Only allowed to return move when `self.colour == self.baord.turn`
        """
        pass

    def undo_move(self, move: chess.Move) -> str:
        """
        This is called when the other player wants to undo a move. If
        `"break"` is returned the undo process will stop.
        """
        return None

    def redo_move(self, move: chess.Move) -> str:
        """
        This is called when a player wants to redo a move. If
        `"break"` is returned the redo process will stop.
        """
        return None

    def open_game(self, pgn: str) -> str:
        """
        This is called when the user desides to open a game. To
        disallow this action return `"break"`
        """
        return None
