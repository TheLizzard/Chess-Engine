import chess
import time

from player import Player
from position import Position


class User(Player):
    def __init__(self, guiboard, board, master, colour, callback=None):
        super().__init__(board=board, colour=colour)
        self.board = board
        self.master = master
        self.mouse_down = False
        self.callback = callback
        self.guiboard = guiboard
        self.piece_selected = None
        self.alowed_to_play = False
        self.available_move_dots = []
        self.user_created_helpers = {}
        self.user_helper_making = None
        self.moved_selected_piece = False
        self.user_created_arrow_start = None
        self.colour = self.colour_to_bool(colour)
        self.bind_mouse()

        self.create_piece = self.guiboard.create_piece
        self.settings = self.guiboard.settings
        self.update = self.guiboard.update
        self.root = self.guiboard.root
        self.size = self.guiboard.size

        self.debug = []

    def go(self):
        pass
        #if self.board.is_game_over():
        #    return None

    def bind_mouse(self):
        for n in (1, 3):
            for i in ("<Button-%d>", "<B%d-Motion>", "<ButtonRelease-%d>"):
                self.master.bind(i%n, self.mouse, True)

    def destroy(self):
        self.remove_available_moves()
        print("please del me. I can't unbind")
        super().destroy()

    def mouse(self, event):
        if not self.alowed_to_play:
            return None
        # name can be one of: (ButtonPress, ButtonRelease, Motion)
        name = event.type._name_
        x = event.x
        y = event.y
        x_out_of_bounds = not (0 < x < self.size*8)
        y_out_of_bounds = not (0 < y < self.size*8)

        if not (self.colour == self.board.turn):
            return None
        if x_out_of_bounds or y_out_of_bounds:
            self.unselect()
            self.update()
            self.master.delete(self.user_helper_making)
            return None

        if event.num == 1:
            if name == "ButtonPress":
                self.delete_object()
                self.moved_selected_piece = False
                self.mouse_down = True
                position = Position.from_coords((x, y))
                if self.piece_selected is not None:
                    self.move_selected((event.x, event.y))
                    self.unselect()
                else:
                    self.select(position)
            elif name == "ButtonRelease":
                self.mouse_down = False
                if self.piece_selected is not None:
                    self.move_selected((event.x, event.y))
        elif event.num == 3:
            if self.mouse_down:
                pass
            elif name == "ButtonPress":
                position = Position.from_coords((x, y))
                self.user_created_arrow_start = position
                self.user_helper_making = self.create_ring(position)
            elif name == "ButtonRelease":
                start = self.user_created_arrow_start
                end = Position.from_coords((x, y))
                if start == end:
                    _hash = hash(start*2)
                    if _hash in self.user_created_helpers:
                        self.delete_object(_hash)
                        self.master.delete(self.user_helper_making)
                    else:
                        ring = self.user_helper_making
                        self.user_created_helpers.update({_hash: ring})
                else:
                    _hash = hash(start+end)
                    if _hash in self.user_created_helpers:
                        self.delete_object(_hash)
                        self.master.delete(self.user_helper_making)
                    else:
                        arrow = self.user_helper_making
                        self.user_created_helpers.update({_hash: arrow})
        elif name == "Motion":
            self.debug.append(event)
            if event.state & 256: # Button 1
                if (self.piece_selected is not None) and self.mouse_down:
                    self.piece_selected.place((x, y))
                    position = Position.from_coords((x, y))
                    if position != self.piece_selected.position:
                        self.moved_selected_piece = True
            elif event.state & 1024: # Button 3
                if not self.mouse_down:
                    start = self.user_created_arrow_start
                    end = Position.from_coords((x, y))
                    if start == end:
                        self.master.delete(self.user_helper_making)
                        self.user_helper_making = self.create_ring(start)
                    else:
                        self.master.delete(self.user_helper_making)
                        self.user_helper_making = self.create_arrow(start, end)

    def delete_object(self, idx=None):
        if idx is None:
            for _, i in self.user_created_helpers.items():
                self.master.delete(i)
            self.user_created_helpers = {}
        else:
            self.master.delete(self.user_created_helpers[idx])
            del self.user_created_helpers[idx]

    def create_ring(self, position):
        coords = position.to_coords()
        colour = self.settings.ring_colour
        width = self.settings.ring_width
        radius = self.settings.ring_radius
        return self._create_circle_arc(*coords, style="arc", r=radius, end=629,
                                       outline=colour, width=width, start=270)

    def create_arrow(self, position1, position2):
        coords1 = position1.to_coords()
        coords2 = position2.to_coords()
        width = self.settings.arrow_width
        colour = self.settings.arrow_colour
        return self.master.create_line(*coords1, *coords2, arrow="last",
                                       fill=colour, width=width)

    def _create_circle_arc(self, x, y, r, **kwargs):
        if "start" in kwargs and "end" in kwargs:
            kwargs["extent"] = kwargs["end"] - kwargs["start"]
            del kwargs["end"]
        return self.master.create_arc(x-r, y-r, x+r, y+r, **kwargs)

    def move_selected(self, new_coords):
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
                self.guiboard.push(move)
                self.delete_object()
                self.remove_available_moves()
                if self.callback is not None:
                    self.callback()
            self.unselect()
        self.update()

    def select(self, position):
        piece_selected = self.guiboard.position_to_piece(position)
        if piece_selected is not None:
            colour = self.colour_to_bool(piece_selected.colour)
            if colour == self.board.turn:
                self.piece_selected = piece_selected
                self.show_available_moves()
                return True
        self.unselect()
        return False

    def unselect(self):
        self.piece_selected = None
        self.remove_available_moves()

    def show_available_moves(self):
        piece = self.piece_selected
        for move in self.board.legal_moves:
            if move.from_square == piece.position.to_int():
                position = Position.from_int(move.to_square)
                if self.guiboard.position_to_piece(position) is None:
                    self.draw_available_move(position)

    def remove_available_moves(self):
        for dot in self.available_move_dots:
            self.master.delete(dot)

    def draw_available_move(self, position):
        radius = self.size/9
        dot = self.draw_dot(position, radius, outline="grey", fill="grey")
        self.available_move_dots.append(dot)

    def draw_dot(self, position, radius, **kwargs):
        x, y = position.to_coords()
        r = radius
        return self.master.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def legal_promoting(self, uci, new_position):
        if self.piece_selected.name == "pawn":
            if (new_position[1] == 8) or (new_position[1] == 1):
                potential_move = chess.Move.from_uci(uci+"q")
                return (potential_move in self.board.legal_moves)
        return False

    def askuser_pawn_promotion(self):
        self.stop()
        master = self.master
        self.chosen_promotion = None
        x1, y1 = (2*self.size, 3*self.size)
        x2, y2 = (x1+4*self.size, y1+2*self.size)
        rectangle = master.create_rectangle((x1, y1, x2, y2), fill="black",
                                            outline="red", width=3)
        x, y = (4*self.size, 3.5*self.size)
        text = "What do you want to promote to?"
        font = self.settings.font
        text = master.create_text((x, y), text=text, fill="white", font=font)
        q = self.create_piece(name="queen", colour="white", position=(3, 4))
        r = self.create_piece(name="rook", colour="white", position=(4, 4))
        b = self.create_piece(name="bishop", colour="white", position=(5, 4))
        n = self.create_piece(name="knight", colour="white", position=(6, 4))
        q.show(), r.show(), b.show(), n.show()
        self.master.bind("<Button-1>", self.promote, True)
        while self.chosen_promotion is None:
            self.root.update()
        q.destroy(), r.destroy(), b.destroy(), n.destroy()
        self.master.delete(rectangle)
        self.master.delete(text)
        self.start()
        return self.chosen_promotion

    def promote(self, event):
        promotions = ("q", "r", "b", "n")
        position = Position.from_coords((event.x, event.y))
        if position[1] == 4:
            if 3 <= position[0] <= 6:
                self.chosen_promotion = promotions[position[0]-3]
