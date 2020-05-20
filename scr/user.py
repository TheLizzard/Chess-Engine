import chess
from player import Player
import time


class User(Player):
    def __init__(self, guiboard, board, master, colour, control):
        super().__init__(board=board, colour=colour)
        self.copy_all_methods(guiboard)
        self.board = board
        self.master = master
        self.control = control
        self.mouse_down = False
        self.guiboard = guiboard
        self.piece_selected = None
        self.alowed_to_play = False
        self.available_move_dots = []
        self.colour = self.colour_to_bool(colour)
        self.bind_mouse()
        self.my_turn = (self.colour == self.board.turn)

    def go(self):
        if self.board.is_game_over():
            return None
        self.my_turn = True
        if self.control:
            while self.my_turn:
                self.master.update()
                time.sleep(0.01)

    def copy_all_methods(self, source):
        target = self
        for attribute in dir(source):
            if attribute[0] != "_":
                method = source.__getattribute__(attribute)
                setattr(target, attribute, method)

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
        if name == "ButtonPress":
            position = self.coords_to_position((x, y))
            self.piece_selected = self.position_to_piece(position)
            if self.piece_selected is not None:
                colour = self.colour_to_bool(self.piece_selected.colour)
                if colour != self.board.turn:
                    self.piece_selected = None
                else:
                    self.show_available_moves()
        elif name == "Motion":
            if self.piece_selected is not None:
                self.piece_selected.place((x, y))
        elif name == "ButtonRelease":
            if self.piece_selected is not None:
                coords = self.master.coords(self.piece_selected.tkcanvasnum)
                if coords != []:
                    new_position = self.coords_to_position(coords)
                    old_position = self.piece_selected.position

                    if new_position != old_position:
                        uci = self.positions_to_uci(old_position, new_position)
                        if self.piece_selected.name == "pawn":
                            if self.legal_promoting(uci, new_position):
                                uci += self.askuser_pawn_promotion()
                        move = chess.Move.from_uci(uci)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            self.my_turn = False
                self.piece_selected = None
                self.remove_available_moves()
                self.update()

    def show_available_moves(self):
        piece = self.piece_selected
        for move in self.board.legal_moves:
            if move.from_square == self.position_to_int(piece.position):
                position = self.int_to_position(move.to_square)
                if self.position_to_piece(position) is None:
                    self.draw_available_move(position)

    def remove_available_moves(self):
        for dot in self.available_move_dots:
            self.master.delete(dot)

    def draw_available_move(self, position):
        place = self.position_to_coords(position)
        radius = self.settings.dot_radius
        dot = self.draw_dot(place, radius, outline="grey", fill="grey")
        self.available_move_dots.append(dot)

    def draw_dot(self, position, radius, **kwargs):
        x, y = position
        r = radius
        return self.master.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def legal_promoting(self, uci, new_position):
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
        position = self.coords_to_position((event.x, event.y))
        if position[1] == 4:
            if 3 <= position[0] <= 6:
                self.chosen_promotion = promotions[position[0]-3]
