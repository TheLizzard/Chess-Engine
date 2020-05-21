import chess
import time

from player import Player
from position import Position


class User(Player):
    def __init__(self, guiboard, board, master, colour, control):
        super().__init__(board=board, colour=colour)
        self.board = board
        self.master = master
        self.control = control
        self.mouse_down = False
        self.guiboard = guiboard
        self.piece_selected = None
        self.alowed_to_play = False
        self.available_move_dots = []
        self.moved_selected_piece = False
        self.colour = self.colour_to_bool(colour)
        self.my_turn = (self.colour == self.board.turn)
        self.bind_mouse()

        self.create_piece = self.guiboard.create_piece
        self.settings = self.guiboard.settings
        self.update = self.guiboard.update
        self.root = self.guiboard.root
        self.size = self.guiboard.size

    def go(self):
        if self.board.is_game_over():
            return None
        self.my_turn = True
        if self.control:
            while self.my_turn:
                self.master.update()
                time.sleep(0.01)

    def bind_mouse(self):
        self.master.bind("<Button-1>", self.mouse, True)
        self.master.bind("<Button-3>", self.mouse, True)
        self.master.bind("<B1-Motion>", self.mouse, True)
        self.master.bind("<B3-Motion>", self.mouse, True)
        self.master.bind("<ButtonRelease-1>", self.mouse, True)
        self.master.bind("<ButtonRelease-3>", self.mouse, True)

    def destroy(self):
        self.remove_available_moves()
        self.unbind()
        self.my_turn = False
        super().destroy()

    def unbind(self):
        self.master.unbind("<Button-1>")
        self.master.unbind("<Button-3>")
        self.master.unbind("<B1-Motion>")
        self.master.unbind("<B3-Motion>")
        self.master.unbind("<ButtonRelease-1>")
        self.master.unbind("<ButtonRelease-3>")

    def mouse(self, event):
        if not self.alowed_to_play:
            return None
        if (not self.my_turn) and self.control:
            return None
        # name can be one of: (ButtonPress, ButtonRelease, Motion)
        name = event.type._name_
        x = event.x
        y = event.y
        if not self.colour:return None
        if name == "ButtonPress":
            self.moved_selected_piece = False
            self.mouse_down = True
            position = Position.from_coords((x, y))
            if self.piece_selected is not None:
                self.move_selected((event.x, event.y))
                self.unselect()
            self.select(position)
        elif name == "Motion":
            if (self.piece_selected is not None) and self.mouse_down:
                self.piece_selected.place((x, y))
                self.moved_selected_piece = True
        elif name == "ButtonRelease":
            self.mouse_down = False
            if self.piece_selected is not None:
                self.move_selected((event.x, event.y))
            self.moved_selected_piece = False

    def move_selected(self, new_coords):
        x_out_of_bounds = not (0 < new_coords[0] < self.size*8)
        y_out_of_bounds = not (0 < new_coords[1] < self.size*8)
        out_of_bounds = x_out_of_bounds or y_out_of_bounds

        new_position = Position.from_coords(new_coords)
        old_position = self.piece_selected.position

        if new_position == old_position:
            if self.moved_selected_piece:
                self.unselect()
        else:
            if not out_of_bounds:
                uci = old_position + new_position
                if self.legal_promoting(uci, new_position):
                    uci += self.askuser_pawn_promotion()
                move = chess.Move.from_uci(uci)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.my_turn = False
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
        self.piece_selected = None
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
        radius = self.settings.dot_radius
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
        self.alowed_to_play = False
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
        self.bind_mouse()
        q.destroy(), r.destroy(), b.destroy(), n.destroy()
        self.master.delete(rectangle)
        self.master.delete(text)
        self.alowed_to_play = True
        self.remove_available_moves()
        return self.chosen_promotion

    def promote(self, event):
        promotions = ("q", "r", "b", "n")
        position = Position.from_coords((event.x, event.y))
        if position[1] == 4:
            if 3 <= position[0] <= 6:
                self.chosen_promotion = promotions[position[0]-3]
