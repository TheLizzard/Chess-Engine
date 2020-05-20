from ScrollBar import AutoScrollbar
from settings import Settings
from licence import Licence
from board import GUIBoard
from help import Help

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
        self.modified_widget_kwargs.pop("justify", None)
        self.set_up_board()
        self.set_up_eval()
        self.set_up_suggestedmoves()
        self.set_up_movehistory()
        self.set_up_playbutton()

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
                command = partial(self.play, event)
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
                                bg=bg, justify="left",
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

        sbar = AutoScrollbar(self.movehistory_frame, self.movehistory_text,
                             command=self.movehistory_text.yview)
        self.movehistory_text["yscrollcommand"] = sbar.set
        sbar.pack(side="right", expand=True, fill="y")

    def set_up_playbutton(self):
        settings = self.user_settings.playbutton
        fg = settings.colour
        bg = settings.background
        command = partial(self.play, "eval.playbutton")
        login_button = tk.Button(self.eval_frame, fg=fg, bg=bg, text="Play",
                                 command=command, **self.modified_widget_kwargs)
        login_button.pack(side="right")

    def play(self, event):
        event = event.split(".")
        if event[0] == "file":
            self.file(event[1])
        if event[0] == "view":
            self.view(event[1])
        if event[0] == "help":
            self.help(event[1])
        print("playing", event)

    def file(self, event):
        if event == "exit":
            self.root.destroy()

    def view(self, event):
        if event == "current_fen":
            self.show_fen()
        elif event == "game_pgn":
            self.show_pgn()

    def help(self, event):
        if event == "licence":
            self.show_licence()
        elif event == "help":
            self.show_help()

    def show_fen(self):
        print("showing fen")

    def show_licence(self):
        Licence()

    def show_help(self):
        Help()

    def set_up_board(self):
        self.board = GUIBoard(settings=self.user_settings.gameboard,
                              root=self.root,
                              kwargs=self.modified_widget_kwargs)

    def update_board(self):
        self.board.update()


a = App()
