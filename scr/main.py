from settings import Settings
from board import GUIBoard
import widgets
from analyse import Analyse

from functools import partial
import tkinter as tk
import threading
import time

SETTINGS = Settings()


class App:
    def __init__(self):
        self.file_open = None
        self.analysing = False
        self.analyses = None
        self.allowed_analyses = True
        self.done_set_up = False
        self.allowed_undo = [True, True]
        self.set_up_tk()
        self.board.update()
        self.done_set_up = True
        self.undone_move_stack = []
        self.root.update()
        self.start_analysing()

    def set_up_tk(self):
        self.root = widgets.Tk()
        self.root.bind_update(self.update)
        self.root.resizable(False, False)
        self.root.title("Chess.py")
        self.root.config(bg=SETTINGS.root.background)
        self.set_up_menu()
        self.root.config(menu=self.menubar)

        self.widget_kwargs = SETTINGS.widgets
        self.modified_widget_kwargs = self.widget_kwargs.dict()
        self.justify = self.modified_widget_kwargs.pop("justify", None)
        self.set_up_board()
        self.set_up_eval()
        self.set_up_suggestedmoves()
        self.set_up_movehistory()
        self.bind_keys()

    def bind_keys(self):
        self.root.bind("<Control-z>", self.undo_move)
        self.root.bind("<Control-Shift-Z>", self.redo_move)

    def set_up_menu(self):
        tearoff = SETTINGS.menu.tearoff
        self.menubar = tk.Menu(self.root, tearoff=tearoff)

        SETTINGS.menu.pop("tearoff")

        for name, _list in SETTINGS.menu.items():
            name = name[0].upper()+name[1:]
            self.submenu = tk.Menu(self.menubar, tearoff=tearoff)
            self.menubar.add_cascade(label=name, menu=self.submenu)
            for button in _list:
                if button.replace("-", "") == "":
                    self.submenu.add_separator()
                    continue
                button = button[0].upper()+button[1:]
                event = (name+"."+button).lower().replace(" ", "_")
                command = partial(self.menu, event)
                self.submenu.add_command(label=button, command=command)

    def set_up_eval(self):
        settings = SETTINGS.evaluation
        width = settings.width
        height = settings.height
        fg = settings.colour
        bg = settings.background
        font = settings.font

        self.eval_frame = tk.Frame(self.root, width=width, height=height,
                                   bg=bg, **self.modified_widget_kwargs)

        self.eval_frame.grid(row=1, column=2)
        self.eval_frame.grid_propagate(False)
        self.eval_frame.pack_propagate(False)

        self.eval_text = tk.Label(self.eval_frame, fg=fg, bg=bg, font=font,
                                  **self.modified_widget_kwargs)
        self.eval_text.grid(row=1, column=1, sticky="news")
        self.eval_text.config(text="2.2")

    def set_up_suggestedmoves(self):
        settings = SETTINGS.suggestedmoves
        fg = settings.colour
        bg = settings.background
        font = settings.font

        self.suggestedmoves_text = tk.Label(self.eval_frame, fg=fg, font=font,
                                            bg=bg, justify=self.justify,
                                            **self.modified_widget_kwargs)
        self.suggestedmoves_text.grid(row=2, column=1, sticky="news")
        self.suggestedmoves_text.config(text="No moves to suggest")

    def set_up_movehistory(self):
        settings = SETTINGS.movehistory
        width = settings.width
        height = settings.height
        fg = settings.colour
        bg = settings.background
        cursor_colour = settings.cursor_colour
        font = settings.font
        self.movehistory_frame = tk.Frame(self.root, width=width,
                                          height=height, bg=bg,
                                          **self.modified_widget_kwargs)
        self.movehistory_frame.grid(row=3, column=2, sticky="news")

        self.movehistory_frame.grid_propagate(False)
        self.movehistory_frame.pack_propagate(False)
        self.movehistory_frame.columnconfigure(0, weight=10)

        width = settings.line_width
        height = settings.line_height

        self.movehistory_text = tk.Text(self.movehistory_frame, height=height,
                                        width=width, font=font, fg=fg, bg=bg,
                                        insertbackground=cursor_colour,
                                        state="disabled",
                                        **self.modified_widget_kwargs)

        self.movehistory_text.pack(side="left", expand=True, fill="y")

        sbar = widgets.AutoScrollbar(self.movehistory_frame,
                                     self.movehistory_text,
                                     command=self.movehistory_text.yview)
        self.movehistory_text["yscrollcommand"] = sbar.set
        sbar.pack(side="right", expand=True, fill="y")

    def menu(self, event):
        event = event.split(".")
        if event[0] == "file":
            self.file(event[1])

        elif event[0] == "edit":
            self.edit(event[1])

        elif event[0] == "view":
            self.view(event[1])

        elif event[0] == "game":
            self.start_game(event[1])

        elif event[0] == "settings":
            self.change_settings(event[1])

        elif event[0] == "help":
            if event[1] == "licence":
                widgets.LicenceWindow()
            elif event[1] == "help":
                widgets.HelpWindow()

        else:
            print("? ", event)

    def file(self, event):
        if event == "open":
            print("file.open")

        elif event == "save":
            print("file.save")

        elif event == "save_as":
            print("file.save_as")

        elif event == "exit":
            self.root.destroy()

        else:
            print("? ", event)

    def edit(self, event):
        if event == "undo_move":
            self.undo_move()

        elif event == "redo_move":
            self.redo_move()

        elif event == "change_position":
            print("edit.change_position")

        else:
            print("? ", event)

    def view(self, event):
        if event == "current_fen":
            w = widgets.CopyableTextWindow()
            w.set(self.board.fen())

        elif event == "game_pgn":
            w = widgets.CopyableTextWindow()
            w.set(self.board.pgn())

    def undo_move(self, event=None):
        if len(self.board.move_stack) > 0:
            move = self.board.undo_move()
            if move != "break":
                self.undone_move_stack.append(move)
                self.moved(clear_undo_stack=False)
                if (event != "go") and self.board.double_undo_redo:
                    self.undo_move("go")
                else:
                    self.board.update()
                    self.board.start_player()

    def redo_move(self, event=None):
        if len(self.undone_move_stack) != 0:
            move = self.undone_move_stack.pop()
            if self.board.redo_move(move) == "break":
                self.undone_move_stack.append(move)
            else:
                self.moved(clear_undo_stack=False)
                if (event != "go") and self.board.double_undo_redo:
                    self.redo_move("go")
                else:
                    self.board.update()
                    self.board.start_player()

    def start_game(self, event):
        if event == "evaluate":
            if self.allowed_analyses:
                self.start_analysing()

        elif event == "play_vs_computer":
            self.allowed_analyses = False
            self.stop_analysing()
            self.clear_pgn()
            colour = self.board.ask_if_user_white()
            self.board.start_comp_v_hum(colour)

        elif event == "play_vs_human":
            self.allowed_analyses = True
            self.stop_analysing()
            self.clear_pgn()
            self.board.start_hum_v_hum()

        elif event == "play_vs_ai":
            self.allowed_analyses = False
            self.stop_analysing()
            self.clear_pgn()
            colour = self.board.ask_if_user_white()
            self.board.start_ai_v_hum(colour)

        elif event == "play_multiplayer":
            self.allowed_analyses = False
            self.stop_analysing()
            self.clear_pgn()
            self.board.start_multiplayer()

    def change_settings(self, event):
        if event == "game_settings":
            print("settings.game_settings")

        elif event == "suggested_moves_settings":
            print("settings.suggested_moves_settings")

    def set_up_board(self):
        self.board = GUIBoard(root=self.root, move_callback=self.moved,
                              undo=self.allowed_undo,
                              kwargs=self.modified_widget_kwargs)

    def update(self):
        if self.done_set_up and self.analysing and (self.analyses is not None):
            score = self.analyses.score
            moves = self.analyses.moves

            if (score is None) or (moves is None):
                return None

            score = score.white()#.score(mate_score=10000)
            score = str(score).replace("+", "")
            moves = self.board.moves_to_san(moves)[:4]

            self.eval_text.config(text=score)
            self.suggestedmoves_text.config(text=" ".join(moves))

    def update_pgn(self):
        self.movehistory_text.config(state="normal")
        old_pgn = self.movehistory_text.get("1.0", "end")[:-1]
        new_pgn = self.board.pgn()
        diff, c = self.find_diff_pgn(old_pgn, new_pgn)
        if c is not None:
            self.clear_pgn()
        self.movehistory_text.insert("end", diff)
        self.movehistory_text.config(state="disabled")

    def clear_pgn(self):
        self.movehistory_text.delete("0.0", "end")

    def moved(self, clear_undo_stack=True):
        if clear_undo_stack:
            self.undone_move_stack = []
        try:
            self.update_pgn()
        except:
            raise
        if self.analysing:
            self.analyses.kill()
            self.start_analysing()

    def find_diff_pgn(self, pgn1, pgn2):
        if pgn1 == "\n":
            pgn1 = ""
        if pgn1 not in pgn2:
            return pgn2, "clear"
        return pgn2[len(pgn1)-len(pgn2):][:-1], None

    def start_analysing(self):
        if self.allowed_analyses:
            self.analysing = True
            self.analyses = Analyse(self.board.board)
            self.analyses.start()

    def stop_analysing(self):
        self.analysing = False
        if self.analyses is not None:
            self.analyses.kill()
        self.eval_frame.grid_remove()


a = App()
while True:
    a.root.update()
    time.sleep(0.1)
