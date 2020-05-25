from settings import Settings
from board import GUIBoard
import widgets
from analyse import Analyse

from functools import partial
import tkinter as tk
import threading
import time


class App:
    def __init__(self):
        self.settings = Settings()
        self.analysing = False
        self.analyses = None
        self.done_set_up = False
        self.set_up_tk()
        self.update_board()
        self.done_set_up = True
        self.root.update()
        self.start_analysing()

    def set_up_tk(self):
        self.root = widgets.Tk()
        self.root.bind_update(self.update)
        self.root.resizable(False, False)
        self.root.title("Chess.py")
        self.root.config(bg="black")
        self.set_up_menu()
        self.root.config(menu=self.menubar)

        self.widget_kwargs = self.settings.widgets
        self.modified_widget_kwargs = self.widget_kwargs.dict()
        self.justify = self.modified_widget_kwargs.pop("justify", None)
        self.set_up_board()
        self.set_up_eval()
        self.set_up_suggestedmoves()
        self.set_up_movehistory()

    def set_up_menu(self):
        tearoff = self.settings.menu.tearoff
        self.menubar = tk.Menu(self.root, tearoff=tearoff)

        self.settings.menu.pop("tearoff")

        for name, _list in self.settings.menu.items():
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
        settings = self.settings.evaluation
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
        settings = self.settings.suggestedmoves
        fg = settings.colour
        bg = settings.background
        font = settings.font

        self.suggestedmoves_text = tk.Label(self.eval_frame, fg=fg, font=font,
                                            bg=bg, justify=self.justify,
                                            **self.modified_widget_kwargs)
        self.suggestedmoves_text.grid(row=2, column=1, sticky="news")
        self.suggestedmoves_text.config(text="No moves to suggest")

    def set_up_movehistory(self):
        settings = self.settings.movehistory
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
            self.help(event[1])

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
            print("edit.undo_move")

        elif event == "redo_move":
            print("edit.redo_move")

        elif event == "change_position":
            print("edit.change_position")

        else:
            print("? ", event)

    def view(self, event):
        if event == "current_fen":
            self.show_fen()

        elif event == "game_pgn":
            self.show_pgn()

    def start_game(self, event):
        if event == "evaluate":
            self.start_analysing()
            print("game.evaluate")

        elif event == "play_vs_computer":
            self.stop_analysing()
            colour = self.ask_if_user_white()
            self.board.start_comp_v_hum(1-colour)

        elif event == "play_vs_human":
            self.stop_analysing()
            self.board.start_hum_v_hum()

        elif event == "play_vs_ai":
            self.stop_analysing()
            colour = self.ask_if_user_white()
            self.board.start_ai_v_hum(1-colour)

        elif event == "play_multiplayer":
            self.stop_analysing()
            print("game.play_multiplayer")

    def change_settings(self, event):
        if event == "game_settings":
            print("settings.game_settings")

        elif event == "suggested_moves_settings":
            print("settings.suggested_moves_settings")

    def help(self, event):
        if event == "licence":
            self.show_licence()
        elif event == "help":
            self.show_help()

    def ask_if_user_white(self):
        return self.board.ask_if_user_white()

    def show_fen(self):
        w = widgets.CopyableEntryWindow()
        w.set(self.board.fen())

    def show_pgn(self):
        w = widgets.CopyableTextWindow()
        w.set(self.pgn())

    def pgn(self):
        return self.board.pgn()

    def show_licence(self):
        widgets.LicenceWindow()

    def show_help(self):
        widgets.HelpWindow()

    def set_up_board(self):
        self.board = GUIBoard(settings=self.settings.gameboard,
                              root=self.root, move_callback=self.moved,
                              kwargs=self.modified_widget_kwargs)

    def update_board(self):
        self.board.update()

    def update(self):
        if self.done_set_up and self.analysing:
            if self.analyses is not None:
                score = self.analyses.score
                moves = self.analyses.moves

                if (score is None) or (moves is None):
                    return None

                try:
                    score = score.white().score(mate_score=10000)
                    moves = self.board.moves_to_san(moves)[:4]

                    self.eval_text.config(text=score)
                    self.suggestedmoves_text.config(text=" ".join(moves))
                except Exception as error:
                    pass

    def moved(self):
        self.movehistory_text.config(state="normal")
        old_pgn = self.movehistory_text.get("1.0", "end")[:-1]
        new_pgn = self.pgn()
        diff = self.find_diff_pgn(old_pgn, new_pgn)
        self.movehistory_text.insert("end", diff)
        self.movehistory_text.config(state="disabled")
        self.analyses.kill()
        self.start_analysing()

    def find_diff_pgn(self, pgn1, pgn2):
        if pgn1 == "\n":
            pgn1 = ""
        return pgn2[len(pgn1)-len(pgn2):][:-1]

    def start_analysing(self):
        self.analysing = True
        self.analyses = Analyse(self.board.board)
        thread = threading.Thread(target=self.analyses.start)
        thread.deamon = True
        thread.start()
        self.eval_frame.grid()

    def stop_analysing(self):
        self.analysing = False
        if self.analyses is not None:
            self.analyses.kill()
        self.eval_frame.grid_remove()


a = App()
while True:
    a.root.update()
    time.sleep(0.1)
