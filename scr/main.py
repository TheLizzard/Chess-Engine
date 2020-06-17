from functools import partial
import tkinter as tk
import threading
import time

from settings import Settings
from analyse import Analyse
from board import GUIBoard
import widgets

SETTINGS = Settings()


class App:
    def __init__(self):
        self.filetypes = (("Chess games", "*.pgn"), ("All files", "*.*"))
        self.file_open = None
        self.analysing = False
        self.analyses = None
        self.allowed_analyses = True
        self.done_set_up = False
        self.set_up_tk()
        self.board.update()
        self.done_set_up = True
        self.root.update()
        self.start_analysing()

    def exit(self):
        self.board.kill_player(self.board.players[0])
        self.board.kill_player(self.board.players[1])
        self.stop_analysing()
        self.root.quit()
        self.root.destroy()
        del self.board
        del self

    def set_up_tk(self):
        """
        Sets up the tkinter part of the program and GUIBoard.
        """
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Chess.py")
        self.root.config(bg=SETTINGS.root.background)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.set_up_menu()
        self.root.config(menu=self.menubar)

        self.widget_kwargs = SETTINGS.widgets
        self.modified_widget_kwargs = self.widget_kwargs.dict()
        self.justify = self.modified_widget_kwargs.pop("justify", None)
        self.board = GUIBoard(root=self.root, move_callback=self.moved,
                              kwargs=self.modified_widget_kwargs)
        self.set_up_eval()
        self.set_up_suggestedmoves()
        self.set_up_movehistory()
        self.bind_keys()

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
            self.open()

        elif event == "save":
            self.save()

        elif event == "save_as":
            self.save_as()

        elif event == "exit":
            self.root.destroy()

        else:
            print("? ", event)

    def bind_keys(self):
        self.root.bind("<Control-s>", self.save)
        self.root.bind("<Control-o>", self.open)
        self.root.bind("<Control-Shift-S>", self.save_as)

    def open(self, _=None) -> None:
        self.open_from_file()

    def open_from_file(self) -> None:
        filename = widgets.askopen(filetypes=self.filetypes)
        if (filename != ()) and (filename != ""):
            with open(filename, "r") as file:
                data = file.read()
            if self.board.set_pgn(data) == "break":
                return "break" # If the players rejected the open
            self.file_open = filename
            self.clear_pgn()
            self.restart_analysing()

    def save_as(self, _=None) -> None:
        filename = widgets.asksave(filetypes=self.filetypes)
        if (filename != ()) and (filename != ""):
            self.file_open = filename
            self.save_to_file()

    def save(self, _=None) -> None:
        if self.file_open is None:
            self.save_as()
        else:
            self.save_to_file()

    def save_to_file(self) -> None:
        with open(self.file_open, "w") as file:
            file.write(self.board.pgn())

    def edit(self, event):
        if event == "undo_move":
            self.root.event_generate("<Control-z>")

        elif event == "redo_move":
            self.root.event_generate("<Control-Shift-Z>")

        elif event == "change_position":
            print("edit.change_position")

        else:
            print("? ", event)

    def view(self, event):
        if event == "current_fen":
            w = widgets.CopyableEntryWindow(width=40)
            w.set(self.board.fen())

        elif event == "game_pgn":
            w = widgets.CopyableTextWindow()
            w.set(self.board.pgn())

    def start_game(self, event):
        if event == "evaluate":
            # This is only active when `self.allowed_analyses` is True
            if self.allowed_analyses:
                # Start analysing the position
                if self.analysing:
                    self.stop_analysing()
                else:
                    self.start_analysing()

        elif event == "play_vs_computer":
            # Add user as `colour` and computer as `not colour`
            colour = self.ask_if_user_white()
            if colour is None:
                return None
            self.board.add_user_as_player(colour)
            self.board.add_computer_as_player(not colour)
            self.reset(False)

        elif event == "play_vs_human":
            # Add the 2 user players and reset the board
            self.board.add_user_as_player(True)
            self.board.add_user_as_player(False)
            self.reset(True)

        elif event == "play_vs_ai":
            # Add user as `colour` and AI as `not colour`
            colour = self.ask_if_user_white()
            if colour is None:
                return None
            self.board.add_user_as_player(colour)
            self.board.add_ai_as_player(not colour)
            self.reset(False)

        elif event == "play_multiplayer":
            # Start multiplayer
            self.board.start_multiplayer()
            self.reset(False)

    def ask_if_user_white(self) -> bool:
        """
        Asks the user what colour they want to play as.
        """
        colour = self.board.ask_user("Do you want to be black or white?",
                               ("white", "black"), (True, False))
        return colour

    def reset(self, allowed_analyses: bool) -> None:
        """
        This resets the board, clears the pgn and sets `allowed_analyses`
        """
        self.allowed_analyses = allowed_analyses
        self.stop_analysing()
        self.clear_pgn()

    def change_settings(self, event):
        if event == "game_settings":
            print("settings.game_settings")

        elif event == "board_settings":
            print("settings.board_settings")

    def update(self):
        if self.done_set_up and self.analysing and (self.analyses is not None):
            self.root.after(500, self.update)
            try:
                score = self.analyses.score.white()#.score(mate_score=10000)
                self.eval_text.config(text=str(score).replace("+", ""))
                moves = self.board.moves_to_san(self.analyses.moves)[:4]
                self.suggestedmoves_text.config(text=" ".join(moves))
            except:
                pass

    def update_pgn(self):
        self.movehistory_text.config(state="normal")
        old_pgn = self.movehistory_text.get("1.0", "end")[:-1]
        new_pgn = self.board.pgn()
        diff, clear = self.find_diff_pgn(old_pgn, new_pgn)
        if clear:
            self.clear_pgn()
        self.movehistory_text.insert("end", diff)
        self.movehistory_text.config(state="disabled")

    def clear_pgn(self):
        self.movehistory_text.delete("0.0", "end")

    def moved(self):
        self.update_pgn()
        self.restart_analysing()

    def find_diff_pgn(self, pgn1, pgn2):
        if pgn1 == "\n":
            pgn1 = ""
        if pgn1 not in pgn2:
            return pgn2, True
        return pgn2[len(pgn1)-len(pgn2):][:-1], False

    def start_analysing(self):
        if (self.allowed_analyses) and (not self.analysing):
            self.analysing = True
            self.analyses = Analyse(self.board.board)
            self.analyses.start()
            self.eval_frame.grid()
            self.update()

    def stop_analysing(self):
        if self.analysing:
            self.analysing = False
            if self.analyses is not None:
                self.analyses.kill()
            self.eval_frame.grid_remove()

    def restart_analysing(self) -> None:
        if self.analysing:
            self.stop_analysing()
            self.start_analysing()


a = App()
a.root.mainloop()
