"""
Defines the User class where the user can move pieces and draw
arrows andrings to help them.

Note:
After calling `User.destroy` you must delete that object because
the tkinter events can't be stoped.
"""


import chess
import time

from .player import Player

from piece import Piece
from position import Position
from settings import Settings


SETTINGS = Settings()
BOARD_SETTINGS = SETTINGS.gameboard
USER_SETTINGS = SETTINGS["gameboard.user"]


class User(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.piece_selected = None
        self.alowed_to_play = False
        self.left_mouse_down = False
        self.right_mouse_down = False
        self.available_move_dots = []
        self.user_created_helpers = {}
        self.user_helper_making = None
        self.moved_selected_piece = False
        self.user_created_arrow_start = None
        self.size = BOARD_SETTINGS.size_of_squares
        self.bind_mouse()

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

    def destroy(self) -> None:
        """
        Destroys everything this class has created.
        Improvement: add a way to unbind the tkinter Events
        """
        self.unselect()
        self.remove_available_moves()
        self.delete_user_created_object()
        self.stop_user_created_object()
        # can't unbind tkinter events so this must be destroyed
        print("please del me. I can't unbind")
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

        if (not (0 < x < self.size*8)) or (not (0 < y < self.size*8)):
            self.unselect()
            self.update()
            self.stop_user_created_object()
            return None

        if event.num == 1:
            if name == "ButtonPress":
                self.delete_user_created_object()
                self.right_mouse_down = True
                self.left_mouse_down = False
                self.moved_selected_piece = False
                position = Position.from_coords((x, y))
                if self.piece_selected is not None:
                    self.move_selected((event.x, event.y))
                    self.unselect()
                else:
                    self.select(position)
            elif name == "ButtonRelease":
                self.right_mouse_down = False
                if self.piece_selected is not None:
                    self.move_selected((event.x, event.y))
        elif event.num == 3:
            if self.right_mouse_down:
                pass
            elif name == "ButtonPress":
                self.left_mouse_down = True
                position = Position.from_coords((x, y))
                self.user_created_arrow_start = position
                self.user_helper_making = self.create_ring(position)
            elif name == "ButtonRelease":
                if not self.left_mouse_down:
                    return None
                self.left_mouse_down = False
                start = self.user_created_arrow_start
                self.user_created_arrow_start = None
                end = Position.from_coords((x, y))
                self.create_user_helping_object(start, end)
        elif name == "Motion":
            if self.user_helper_making is not None:
                self.stop_user_created_object()
            if event.state & 256: # Button 1
                if (self.piece_selected is not None) and self.right_mouse_down:
                    self.piece_selected.place((x, y))
                    position = Position.from_coords((x, y))
                    if position != self.piece_selected.position:
                        self.moved_selected_piece = True
            elif event.state & 1024: # Button 3
                if not self.left_mouse_down:
                    return None
                elif not self.right_mouse_down:
                    start = self.user_created_arrow_start
                    end = Position.from_coords((x, y))
                    if start == end:
                        self.user_helper_making = self.create_ring(start)
                    else:
                        self.user_helper_making = self.create_arrow(start, end)

    def create_user_helping_object(self, start: Postion, end: Postion) -> None:
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
        Used to create an arc. Taken from stackoverflow
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
        new_position = Position.from_coords(new_coords)
        old_position = self.piece_selected.position

        if new_position == old_position:
            if self.moved_selected_piece:
                self.unselect()
        else:
            uci = (old_position + new_position).to_str()
            if self.legal_promoting(uci, new_position):
                uci += self.askuser_pawn_promotion()
            move = chess.Move.from_uci(uci)
            if move in self.board.legal_moves:
                self.delete_user_created_object()
                self.remove_available_moves()
                self.push(move)
            self.unselect()
        self.update()

    def push(self, move: chess.Move) -> None:
        """
        Calls callback with the move as by the board, player protocol
        """
        self.callback(move)

    def select(self, position: Position) -> None:
        """
        Selects the piece the user has clicked.
        """
        piece_selected = self.position_to_piece(position)
        if piece_selected is not None:
            colour = self.colour_to_bool(piece_selected.colour)
            if colour == self.board.turn:
                self.piece_selected = piece_selected
                self.show_available_moves()
                return None
        self.unselect()

    def position_to_piece(self, position: Position) -> Piece:
        for piece in self.pieces:
            if piece.position == position:
                return piece

    def unselect(self):
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

    def legal_promoting(self, uci: str, new_position: Position) -> bool:
        if self.piece_selected.name == "pawn":
            if (new_position[1] == 8) or (new_position[1] == 1):
                potential_move = chess.Move.from_uci(uci+"q")
                return (potential_move in self.board.legal_moves)
        return False

    def askuser_pawn_promotion(self) -> str:
        self.stop()
        master = self.master
        self.chosen_promotion = None
        x1, y1 = (2*self.size, 3*self.size)
        x2, y2 = (x1+4*self.size, y1+2*self.size)
        rectangle = master.create_rectangle((x1, y1, x2, y2), fill="black",
                                            outline="red", width=3)
        x, y = (4*self.size, 3.5*self.size)
        text = "What do you want to promote to?"
        font = USER_SETTINGS.font
        text = master.create_text((x, y), text=text, fill="white", font=font)
        q = self.create_piece(name="queen", colour="white", position=(3, 4))
        r = self.create_piece(name="rook", colour="white", position=(4, 4))
        b = self.create_piece(name="bishop", colour="white", position=(5, 4))
        n = self.create_piece(name="knight", colour="white", position=(6, 4))
        q.show(), r.show(), b.show(), n.show()
        self.master.bind("<Button-1>", self.promote, True)
        while self.chosen_promotion is None:
            self.update(redraw=False)
        q.destroy(), r.destroy(), b.destroy(), n.destroy()
        self.master.delete(rectangle)
        self.master.delete(text)
        self.start()
        return self.chosen_promotion

    def promote(self, event: tk.Event) -> None:
        promotions = ("q", "r", "b", "n")
        position = Position.from_coords((event.x, event.y))
        if position[1] == 4:
            if 3 <= position[0] <= 6:
                self.chosen_promotion = promotions[position[0]-3]

    def undo_move(self, move: chess.Move) -> str:
        self.remove_available_moves()
        self.stop_user_created_object()

    def redo_move(self, move chess.Move) -> str:
        self.remove_available_moves()
        self.stop_user_created_object()

    def create_piece(self, **kwargs) -> Piece:
        kwargs.update({"master": self.master})
        piece = Piece(**kwargs)
        piece.resize_scale(scale=BOARD_SETTINGS.scale_for_pieces)
        return piece
