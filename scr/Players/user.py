#https://stackoverflow.com/questions/15269682/python-tkinter-canvas-fail-to-bind-keyboard
"""
Defines the User class where the user can move pieces and draw
arrows andrings to help them.

Note:
After calling `User.destroy` you must delete that object because
the tkinter events can't be stoped.
"""


import tkinter as tk
import chess
import time

from .player import Player

import widgets
from piece import Piece
from position import Position
from settings import Settings


SETTINGS = Settings()
BOARD_SETTINGS = SETTINGS.gameboard
USER_SETTINGS = SETTINGS["gameboard.user"]


class User(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = BOARD_SETTINGS.size_of_squares
        self.piece_selected = None
        self.left_mouse_down = False
        self.available_move_dots = []
        self.right_mouse_down = False
        self.user_created_helpers = {}
        self.user_helper_making = None
        self.moved_selected_piece = False
        self.user_created_arrow_start = None
        self.bind_mouse()
        self.bind_keys()

    def position_to_piece(self, position: Position) -> Piece:
        for piece in self.pieces:
            if piece.position == position:
                return piece

    def push(self, move: chess.Move) -> None:
        """
        Calls callback with the move as by the board, player protocol
        """
        self.left_mouse_down = False
        self.callback(move)

    def bind_mouse(self) -> None:
        """
        This binds both mouse buttons (left and right) for all 3 events:
            Press
            Release
            Motion
        All of the events go to `self.mouse`
        """
        for n in (1, 3):
            for i in ("<Button-%d>", "<B%d-Motion>", "<ButtonRelease-%d>"):
                self.master.bind(i%n, self.mouse, True)

    def bind_keys(self) -> None:
        """
        This binds the keys that are responsible for undo and redo moves.
        """
        self.master.bind("<Button-1>", self.get_focus, True)
        self.master.bind("<Control-z>", self.send_undo_move)
        self.master.bind("<Control-Shift-Z>", self.send_redo_move)

    def get_focus(self, _):
        """
        This gets keyboard focus on the tkinter canvas so that key bindings
        would work. Taken from StackOverflow
        """
        self.master.focus_set()

    def send_undo_move(self, _) -> None:
        """
        This sends an undo request to GUIBoard through the player board
        protocol
        """
        self.request_undo()

    def send_redo_move(self, _) -> None:
        """
        This sends a redo request to GUIBoard through the player board
        protocol
        """
        self.request_redo()

    def destroy(self) -> None:
        """
        Destroys everything this class has created.
        Improvement: add a way to unbind the tkinter Events
        """
        self.unselect()
        self.remove_available_moves()
        self.delete_user_created_object()
        self.stop_user_created_object()
        super().destroy()

    def mouse(self, event: tk.Event) -> None:
        """
        This takes in all tkinter mouse events and reacts to them.
        """
        if (not self.alowed_to_play) or (self.colour != self.board.turn):
            return None
        # name can be one of: (ButtonPress, ButtonRelease, Motion)
        name = event.type._name_
        x = event.x
        y = event.y
        pos = (x, y)

        if (not (0 < x < self.size*8)) or (not (0 < y < self.size*8)):
            self.unselect()
            self.update()
            self.stop_user_created_object()
        elif event.num == 1:
            self.mouse_left(name, pos)
        elif event.num == 3:
            self.mouse_right(name, pos)
        elif name == "Motion":
            if self.user_helper_making is not None:
                self.stop_user_created_object()
            if event.state & 256: # Button 1
                self.mouse_left("Motion", pos)
            if event.state & 1024: # Button 1
                self.mouse_right("Motion", pos)

    def mouse_left(self, name, pos):
        if name == "ButtonPress":
            self.delete_user_created_object()
            self.right_mouse_down = True
            self.left_mouse_down = False
            self.moved_selected_piece = False
            position = Position.from_coords(pos)
            if self.piece_selected is not None:
                self.move_selected(pos)
                self.unselect()
            else:
                self.select(position)
        elif name == "ButtonRelease":
            self.right_mouse_down = False
            if self.piece_selected is not None:
                self.move_selected(pos)
        elif name == "Motion":
            if (self.piece_selected is not None) and self.right_mouse_down:
                self.piece_selected.place(pos)
                position = Position.from_coords(pos)
                if position != self.piece_selected.position:
                    self.moved_selected_piece = True

    def mouse_right(self, name, pos):
        if self.right_mouse_down:
            pass
        elif name == "ButtonPress":
            self.left_mouse_down = True
            position = Position.from_coords(pos)
            self.user_created_arrow_start = position
            self.user_helper_making = self.create_ring(position)
        elif name == "ButtonRelease":
            if not self.left_mouse_down:
                return None
            self.left_mouse_down = False
            start = self.user_created_arrow_start
            #self.user_created_arrow_start = None
            end = Position.from_coords(pos)
            self.create_user_helping_object(start, end)
        elif name == "Motion":
            if self.left_mouse_down and (not self.right_mouse_down):
                start = self.user_created_arrow_start
                end = Position.from_coords(pos)
                if start == end:
                    self.user_helper_making = self.create_ring(start)
                else:
                    self.user_helper_making = self.create_arrow(start, end)

    def create_user_helping_object(self, start:Position, end:Position) -> None:
        """
        This creates a object that can help the user like:
            rings (can be created by clicking the right mouse button)
            arrows (can be created by dragging the right mouse button)
        To remove all of the objects from the board eather create a new
        object over them or click with the left mouse button.
        """
        if start == end:
            _hash = hash(start*2)
            if _hash in self.user_created_helpers:
                self.delete_user_created_object(_hash)
                self.stop_user_created_object()
            else:
                ring = self.user_helper_making
                self.user_created_helpers.update({_hash: ring})
        else:
            _hash = hash(start+end)
            if _hash in self.user_created_helpers:
                self.delete_user_created_object(_hash)
                self.stop_user_created_object()
            else:
                arrow = self.user_helper_making
                self.user_created_helpers.update({_hash: arrow})

    def delete_user_created_object(self, idx: int=None) -> None:
        """
        This deletes the objects that help the user like arrows and rings.
        If idx (must come from `position.Move.__hash__`) is specified
        only that one will be deleted.
        Else all of the object will be deleted.
        """
        if idx is None:
            for _, i in self.user_created_helpers.items():
                self.master.delete(i)
            self.user_created_helpers = {}
        else:
            self.master.delete(self.user_created_helpers[idx])
            del self.user_created_helpers[idx]

    def stop_user_created_object(self) -> None:
        """
        Stop the user from creating a helping object.
        This is fix to Issue #7
        """
        if self.user_helper_making is not None:
            self.master.delete(self.user_helper_making)

    def create_ring(self, position: Position) -> None:
        """
        Draws a temporaty ring to help the user.
        """
        coords = position.to_coords()
        colour = USER_SETTINGS.ring_colour
        width = USER_SETTINGS.ring_width
        radius = USER_SETTINGS.ring_radius
        # `start` and `end` are weird numbers because if start is 0 and end is
        # 360 tkinter doesn't draw anything.
        return self._create_circle_arc(*coords, style="arc", r=radius, end=629,
                                       outline=colour, width=width, start=270)

    def create_arrow(self, position1: Position, position2: Position) -> None:
        """
        Draws a temporaty arrow to help the user.
        """
        coords1 = position1.to_coords()
        coords2 = position2.to_coords()
        width = USER_SETTINGS.arrow_width
        colour = USER_SETTINGS.arrow_colour
        return self.master.create_line(*coords1, *coords2, arrow="last",
                                       fill=colour, width=width)

    def _create_circle_arc(self, x: int, y: int, r: int, **kwargs) -> None:
        """
        Used to create an arc. Taken from StackOverflow
        """
        if "start" in kwargs and "end" in kwargs:
            kwargs["extent"] = kwargs["end"] - kwargs["start"]
            del kwargs["end"]
        return self.master.create_arc(x-r, y-r, x+r, y+r, **kwargs)

    def move_selected(self, new_coords: tuple) -> None:
        """
        Moves the selected piece to the new_coords (the argument).
        It checks if the move is legal.
        """
        new = Position.from_coords(new_coords)
        old = self.piece_selected.position

        if new == old:
            if self.moved_selected_piece:
                self.unselect()
                self.update()
            else:
                self.piece_selected.show()
        else:
            promotion = None
            if self.legal_promoting(old, new):
                promotion = self.askuser_pawn_promotion()
            move = chess.Move(int(old), int(new), promotion=promotion)
            if move in self.board.legal_moves:
                self.delete_user_created_object()
                self.remove_available_moves()
                self.push(move)
            self.unselect()
            self.update()

    def select(self, position: Position) -> None:
        """
        Selects the piece the user has clicked.
        """
        piece_selected = self.position_to_piece(position)
        if piece_selected is not None:
            if piece_selected.colour == self.board.turn:
                self.piece_selected = piece_selected
                self.show_available_moves()
                return None
        self.unselect()

    def unselect(self) -> None:
        """
        Unselects the selected piece
        """
        self.piece_selected = None
        self.remove_available_moves()

    def show_available_moves(self) -> None:
        """
        Show the available moves by creating small dots on the board where
        there are legal moves
        """
        piece = self.piece_selected
        for move in self.board.legal_moves:
            if move.from_square == piece.position.to_int():
                position = Position.from_int(move.to_square)
                if self.position_to_piece(position) is None:
                    self.draw_available_move(position)

    def remove_available_moves(self) -> None:
        for dot in self.available_move_dots:
            self.master.delete(dot)

    def draw_available_move(self, position: Position) -> None:
        radius = self.size/9
        colour = USER_SETTINGS.available_moves_dots_colour
        dot = self.draw_dot(position, radius, outline=colour, fill=colour)
        self.available_move_dots.append(dot)

    def draw_dot(self, position, radius, **kwargs):
        x, y = position.to_coords()
        r = radius
        return self.master.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def legal_promoting(self, old: Position, new: Position) -> bool:
        if ((old.y == 7) and (new.y == 8)) or ((old.y == 2) and (new.y == 1)):
            return self.piece_selected.name == "pawn"
        return False

    def askuser_pawn_promotion(self) -> str:
        self.stop()
        root = self.master.winfo_toplevel()
        x, y = root.winfo_x(), root.winfo_y()
        window = widgets.Question(x, y)
        window.ask_user_multichoice("What do you want to promote to?",
                                    ("Queen", "Rook", "Bishop", "Knight"),
                                    mapping=(5, 4, 3, 2))
        chosen_promotion = window.wait()
        window.destroy()
        self.start()
        return chosen_promotion

    def undo_move(self, move: chess.Move) -> str:
        self.remove_available_moves()
        self.stop_user_created_object()

    def redo_move(self, move: chess.Move) -> str:
        self.remove_available_moves()
        self.stop_user_created_object()
