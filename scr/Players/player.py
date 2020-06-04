"""
Defines the Player class that can be inherited from.
"""


class Player:
    def __init__(self, board, master, colour, pieces, update, callback,
                 debug=False):
        """
 ---------------- -------------------- ---------------------------------------- 
| Variable       | Type               | Further info                           |
 ---------------- -------------------- ---------------------------------------- 
| self.board     | chess.Board object | Never push moves, call self.callback   |
| self.master    | tk.Canvas object   | Will be deprecated in the future       |
| self.tk_object | a tk widget object | Used only for `widget.after()`         |
| self.colour    | bool               | The colour of the player               |
| self.pieces    | [piece.Piece, ...] | The pieces on GUIBoard (deprecated)    |
| self.debug     | bool               | Used only in testing                   |
| self.callback  | function           | use: `self.callback(move: chess.Move)` |
| self.update    | function           | use: `self.update(redraw: bool)`       |
 ---------------- -------------------- ---------------------------------------- 
        """
        self.board = board
        self.master = master
        self.tk_object = master
        self.colour = colour
        self.pieces = pieces
        self.update = update
        self.callback = callback
        self.debug = debug

        self.alowed_to_play = False

    def start(self):
        self.alowed_to_play = True

    def stop(self):
        self.alowed_to_play = False

    def destroy(self):
        """
            After this method is called the player must stop immediately.
        """
        self.stop()

    def undo_move(self, move):
        """
            Called when the user wants to undo a move.
            If "break" is returned the undo will be blocked
        """
        pass

    def redo_move(self, move):
        """
            Called when the user wants to redo a move.
            If "break" is returned the redo will be blocked
        """
        pass

    def go(self):
        """
            Called every time the GUIBoard needs the player to move
            Always call with the move `self.callback(move)`
            Only allowed to return move when `self.colour == self.baord.turn`
        """
        pass

    def colour_to_bool(self, colour):
        if isinstance(colour, str):
            return colour == "white"
        else:
            return colour
