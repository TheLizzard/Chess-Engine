from settings import Settings
from board import GUIBoard
import widgets

from functools import partial
import tkinter as tk


class App:
    def __init__(self):
        self.user_settings = Settings()
        self.set_up_tk()
        self.update_board()
        self.root.update()

    def set_up_tk(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Chess.py")
        self.root.config(bg="black")
        self.set_up_menu()
        self.root.config(menu=self.menubar)

        self.widget_kwargs = self.user_settings.widgets
        self.modified_widget_kwargs = self.widget_kwargs.dict()
        self.justify = self.modified_widget_kwargs.pop("justify", None)
        self.set_up_board()
        self.set_up_eval()
        self.set_up_suggestedmoves()
        self.set_up_movehistory()

    def set_up_menu(self):
        tearoff = self.user_settings.menu.tearoff
        self.menubar = tk.Menu(self.root, tearoff=tearoff)

        self.user_settings.menu.pop("tearoff")

        for name, _list in self.user_settings.menu.items():
            name = name[0].upper()+name[1:]
            self.menu_example = tk.Menu(self.menubar, tearoff=tearoff)
            self.menubar.add_cascade(label=name, menu=self.menu_example)
            for button in _list:
                if button.replace("-", "") == "":
                    self.menu_example.add_separator()
                    continue
                button = button[0].upper()+button[1:]
                event = (name+"."+button).lower().replace(" ", "_")
                command = partial(self.menu, event)
                self.menu_example.add_command(label=button, command=command)

    def set_up_eval(self):
        settings = self.user_settings.evaluation
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
        self.eval_text.pack(side="left")

    def set_up_suggestedmoves(self):
        settings = self.user_settings.suggestedmoves
        width = settings.width
        height = settings.height
        fg = settings.colour
        bg = settings.background
        font = settings.font
        self.suggestedmoves_frame = tk.Frame(self.root, width=width,
                                             height=height, bg=bg,
                                             **self.modified_widget_kwargs)
        self.suggestedmoves_frame.grid(row=2, column=2)
        self.suggestedmoves_frame.grid_propagate(False)

        n_moves_text = tk.Label(self.suggestedmoves_frame, fg=fg, font=font,
                                bg=bg, justify=self.justify,
                                **self.modified_widget_kwargs)
        n_moves_text.grid(row=1, column=1)

    def set_up_movehistory(self):
        settings = self.user_settings.movehistory
        width = settings.width
        height = settings.height
        fg = settings.colour
        bg = settings.background
        font = settings.font
        self.movehistory_frame = tk.Frame(self.root, width=width,
                                          height=height, bg=bg,
                                          **self.modified_widget_kwargs)
        self.movehistory_frame.grid(row=3, column=2)

        self.movehistory_frame.grid_propagate(False)
        self.movehistory_frame.pack_propagate(False)
        self.movehistory_frame.columnconfigure(0, weight=10)

        width = settings.line_width
        height = settings.line_height

        self.movehistory_text = tk.Text(self.movehistory_frame, height=height,
                                        width=width, font=font, fg=fg, bg=bg,
                                        **self.modified_widget_kwargs)

        self.movehistory_text.pack(side="left", expand=True, fill="y")

        sbar = widgets.AutoScrollbar(self.movehistory_frame,
                                     self.movehistory_text,
                                     command=self.movehistory_text.yview)
        self.movehistory_text["yscrollcommand"] = sbar.set
        sbar.pack(side="right", expand=True, fill="y")=

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
            print("game.evaluate")

        elif event == "play_vs_computer":
            colour = self.ask_if_user_white()
            self.board.start_comp_v_hum(1-colour)

        elif event == "play_vs_human":
            self.board.start_hum_v_hum()

        elif event == "play_vs_ai":
            colour = self.ask_if_user_white()
            self.board.start_ai_v_hum(1-colour)

        elif event == "play_multiplayer":
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
        w.set(self.board.pgn())

    def show_licence(self):
        widgets.LicenceWindow()

    def show_help(self):
        widgets.HelpWindow()

    def set_up_board(self):
        self.board = GUIBoard(settings=self.user_settings.gameboard,
                              root=self.root,
                              kwargs=self.modified_widget_kwargs)

    def update_board(self):
        self.board.update()


a = App()
