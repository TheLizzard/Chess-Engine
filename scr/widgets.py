#https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
from tkinter.filedialog import askopenfilename, asksaveasfilename
from functools import partial
from tkinter import ttk
import tkinter as tk
import threading
import time
import re


"""
This is a simple tk window with a tk text. It doesn't have the top bar.
It also has an "Ok" button that closes the text box
"""
class TextWindow:
    def __init__(self, **kwargs):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        #self.root.wm_attributes("-type", "splash")
        self.text = tk.Text(self.root, **kwargs, font=("Courier New", 10))
        self.sbar = tk.Scrollbar(self.root, command=self.text.yview)
        self.button = tk.Button(self.root, text="Ok", command=self.root.destroy)
        self.text.config(yscrollcommand=self.sbar.set)
        self.text.grid(row=1, column=1, sticky="news")
        self.sbar.grid(row=1, column=2, sticky="news")
        self.button.grid(row=2, column=1, columnspan=2, sticky="news")
        self.disable()
        self.button.focus()
        self.button.bind("<Return>", lambda e:self.root.destroy())

    def disable(self) -> None:
        self.text.config(state="disabled")

    def enable(self) -> None:
        self.text.config(state="normal")

    def insert(self, *args) -> None:
        if self.text["state"] == "disabled":
            self.enable()
        self.text.insert(*args)
        if self.text["state"] == "disabled":
            self.disable()


class CopyableWindow:
    def __init__(self):
        self.root = tk.Tk()
        #self.root.wm_attributes("-type", "splash")
        self.button_c = tk.Button(self.root, text="Copy", command=self.copy)
        self.button = tk.Button(self.root, text="Ok", command=self.root.destroy)
        self.button_c.grid(row=1, column=2, sticky="news")
        self.button.grid(row=2, column=1, columnspan=2, sticky="news")
        self.button.focus()
        self.button.bind("<Return>", lambda e:self.root.destroy())

    def add_widget(self, widget) -> None:
        widget.grid(row=1, column=1, sticky="news")

    def copy(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.get())
        self.root.update()


"""
This is a simple window with a tkinter entry widget that has a copy button.
"""
class CopyableEntryWindow(CopyableWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.text = tk.Entry(self.root, **kwargs)
        super().add_widget(self.text)

    def set(self, string: str) -> None:
        self.widget.insert(0, string)

    def clear(self) -> None:
        self.widget.delete(0, "end")

    def get(self) -> str:
        return self.widget.get()


"""
This is a simple window with a tkinter text widget that has a copy button.
"""
class CopyableTextWindow(CopyableWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.text = tk.Text(self.root, **kwargs)
        super().add_widget(self.text)

    def set(self, string: str) -> None:
        self.text.insert("0.0", string)

    def clear(self) -> None:
        self.text.delete("0.0", "end")

    def get(self) -> str:
        return self.text.get("0.0", "end")


"""
This is an auto hidding scrollbar that needs a tkinter text widget to work.
It supports all 3 geometry managers (pack, place, grid).
"""
class AutoScrollbar(tk.Scrollbar):
    def __init__(self, master, text_widget: tk.Text, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry_manager_kwargs = {}
        self.text_widget = text_widget
        self.geometry_manager = None
        self.hidden = True

    def set(self, low, high) -> None:
        if float(low) <= 0.0 and float(high) >= 1.0:
            if not self.hidden:
                if self.geometry_manager == "grid":
                    self.grid_remove()
                elif self.geometry_manager == "pack":
                    self.pack_forget()
                elif self.geometry_manager == "place":
                    self.place_forget()
                self.text_widget["width"] += 2
                self.hidden = True
        else:
            if self.hidden:
                self.text_widget["width"] -= 2
                if self.geometry_manager == "grid":
                    self.grid(**self.geometry_manager_kwargs)
                elif self.geometry_manager == "pack":
                    self.pack(**self.geometry_manager_kwargs)
                elif self.geometry_manager == "place":
                    self.place(**self.geometry_manager_kwargs)
                self.hidden = False
        super().set(low, high)

    def pack(self, **kwargs) -> None:
        super().pack(**kwargs)
        self.geometry_manager = "pack"
        self.geometry_manager_kwargs = kwargs

    def place(self, **kwargs) -> None:
        super().place(**kwargs)
        self.geometry_manager = "place"
        self.geometry_manager_kwargs = kwargs

    def grid(self, **kwargs) -> None:
        super().grid(**kwargs)
        self.geometry_manager = "grid"
        self.geometry_manager_kwargs = kwargs


class LicenceWindow(TextWindow):
    def __init__(self):
        super().__init__(height=35, width=75)
        self.insert("end", self.get_text())

    def get_text(self) -> str:
        with open("Constants/Licence.txt", "r") as file:
            data = file.read()
        return data

class HelpWindow(TextWindow):
    def __init__(self):
        super().__init__(wrap="word")
        text = self.get_text()
        self.insert("end", text)
        self.config_tags()
        self.style_text(text)
        while self.text.get("end-1l", "end").replace(" ", "") == "\n":
            self.text.delete("end-1l", "end")

    def style_text(self, text: str) -> None:
        ITALIC_REGEX = "![^\n]*!"
        BOLD_REGEX = "#[^\n]*#"
        KEYBOARD_COMBINATION_REGEX = "`[^\n]*`"
        self.add_tag("italic", ITALIC_REGEX)
        self.add_tag("bold", BOLD_REGEX)
        self.add_tag("grey", KEYBOARD_COMBINATION_REGEX)

    def add_tag(self, tag_name: str, regex: str):
        pos = "1.0"
        while True:
            count_var = tk.StringVar(self.root)
            pos = self.text.search(regex, pos, stopindex="end",
                                   count=count_var, regexp=True)
            if pos == "":
                break
            size = count_var.get()
            end = "%s + %sc" % (pos, size)
            end = self.text.index(end)
            self.text.tag_add(tag_name, pos, end)
            self.text.delete(end+"-1c", end)
            self.text.delete(pos, pos+"+1c")
            pos = end+"-2c"

    def config_tags(self) -> None:
        self.text.tag_config("bold", font=("", 12, "bold"))
        self.text.tag_config("grey", background="#EEEEEE")
        self.text.tag_config("italic", font=("", 10, "italic", "underline"))

    def get_text(self) -> str:
        with open("Constants/Help.txt", "r") as file:
            data = file.read()
        output = ""
        for line in data.split("\n"):
            if line.replace(" ", "") == "":
                output += "\n"
            elif line[:2] != "//":
                output += line+"\n"
        return output


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        self.binds = []
        self.highlight_number = 0

        super().__init__(*args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

        self.unbind("<Control-a>")
        self.bind("<Control-KeyRelease-a>", self.select_all)
        self.bind("<Control-v>", self.paste)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args

        if command in ("insert", "delete", "replace"):
            result = self.generate_event(cmd)
            if result == "break":
                return "break"
        try:
            result = self.tk.call(cmd)
        except:
            result = None
        return result

    def generate_event(self, cmd: tuple) -> str:
        for bind in self.binds:
            if bind(cmd) == "break":
                return "break"

    def bind_modified(self, function) -> None:
        if function not in self.binds:
            self.binds.append(function)

    def unbind_modified(self, function) -> None:
        if self.binds.count(function) == 1:
            self.binds.remove(function)

    def paste(self, event: tk.Event) -> None:
        if len(self.tag_ranges("sel")) != 0:
            self.delete("sel.first", "sel.last")

    def select_all(self, event: tk.Event) -> None:
        self.tag_add("sel", "0.0", "end")
        self.mark_set("insert", "end")


"""
Asks the user a question and returns
the result as the answer if mapping isn't defined.
If mapping is defined than that element of the tuple will be returned
Example use:
    board.ask_user("This is the question", ("Answer 1", "Answer 2"),
                   (1, 2))
    # If the user clicks on "Answer 1" than `1` will be returned
    # If the user clicks on "Answer 2" than `2` will be returned
"""
class Question:
    def __init__(self, x: int, y: int):
        self.result = None
        self.running = True
        self.root = tk.Tk()
        self.root.geometry("+%d+%d" % (x, y))
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.resizable(False, False)

    def on_closing(self):
        self.root.quit()
        self.root.destroy()
        self.running = False

    def destroy(self) -> None:
        if self.running:
            self.root.quit()
            self.root.destroy()
            self.running = False

    def get(self):
        return self.result

    def wait(self):
        if self.running:
            self.root.mainloop()
        return self.result

    def add_custom(self, cls, *args, **kwargs) -> None:
        """
        Adds a custom widget with custom args+kwargs at the bottom
        of the window
        """
        widget = cls(self.root, *args, **kwargs)
        widget.grid(column=1, columnspan=10, sticky="news")

    def set_result(self, result) -> None:
        """
        This sets the result variable and ends the `wait` method
        """
        self.result = result
        self.running = False
        self.root.quit()
        self.root.destroy()

    def ask_for_ip(self) -> None:
        font = ("Lucida Console", 18)
        kwargs = {"borderwidth": 0, "highlightthickness": 0}

        text = "What IP do you want to connect to?"
        self.label = tk.Label(self.root, text=text, **kwargs)
        self.label.grid(row=1, column=1, columnspan=2, sticky="news")

        self.entry = CustomText(self.root, height=1, width=15, font=font,
                                **kwargs)
        self.entry.grid(row=2, column=1)
        self.entry.bind_modified(self.check_ip)
        self.entry.focus()

        self.button = tk.Button(self.root, text="Done",
                                command=self._ask_for_ip, **kwargs)
        self.button.grid(row=2, column=2, sticky="news")

    def _ask_for_ip(self) -> None:
        if self.check_ip():
            self.set_result(self.entry.get("0.0", "end").replace("\n", ""))

    def check_ip(self, event: tk.Event=None) -> bool:
        text = self.entry.get("0.0", "end").replace("\n", "")
        if (event is not None) and (event[1] == "insert"):
            new_char = event[3]
            if new_char == "\n":
                self._ask_for_ip()
            if (new_char != ".") and (not new_char.isdigit()):
                return "break"
            else:
                pos = int(self.entry.index("insert").split(".")[1])
                text = text[:pos]+new_char+text[pos:]
        result = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", text)
        if result is None:
            self.entry.config(bg="white")
            return False
        self.entry.config(bg="light green")
        return True

    def ask_user_multichoice(self, question, answers, mapping=None) -> None:
        self.buttons = []
        kwargs = {"borderwidth": 0, "highlightthickness": 0}

        if (mapping is not None) and (len(answers) != len(mapping)):
            raise ValueError("The length of mapping and answer"\
                             "should be the same")

        self.label = tk.Label(self.root, text=question, **kwargs)
        self.label.grid(row=1, column=1, columnspan=len(answers),
                        sticky="news")
        for i, answer in enumerate(answers):
            if mapping is None:
                event = answer
            else:
                event = mapping[i]
            cmd = partial(self._ask_user_multichoice, event)
            button = tk.Button(self.root, text=answer, command=cmd)
            button.grid(row=2, column=i+1, sticky="news")
            self.buttons.append(button)

    def _ask_user_multichoice(self, event) -> None:
        self.set_result(event)

    def ask_user_entry(self, question) -> None:
        commmand = self._ask_user_entry
        self.root.bind("<Return>", commmand)
        self.label = tk.Label(self.root, text=question)
        self.entry = tk.Entry(self.root)
        self.entry.focus()
        self.button = tk.Button(self.root, text="Done", command=commmand)

        self.label.grid(row=1, column=1, columnspan=2, sticky="news")
        self.entry.grid(row=2, column=1, sticky="news")
        self.button.grid(row=2, column=2, sticky="news")

    def _ask_user_entry(self, event=None) -> None:
        self.set_result(self.entry.get())


class ScrolledListboxes(tk.Frame):
    def __init__(self, *args, width=None, **kwargs):
        super().__init__(*args, **kwargs)

        kwargs = {"borderwidth": 0, "highlightthickness": 0}
        self.sbar = tk.Scrollbar(self, command=self.scrollbar_change, **kwargs)
        kwargs.update({"selectbackground": "white", "activestyle": "none",
                       "width": width})
        self.lb1 = tk.Listbox(self, yscrollcommand=self.sbar.set, **kwargs)
        self.sep = ttk.Separator(self, orient="vertical")
        self.lb2 = tk.Listbox(self, yscrollcommand=self.sbar.set, **kwargs)

        self.lb1.grid(row=1, column=1, sticky="news")
        self.sep.grid(row=1, column=2, sticky="news")
        self.lb2.grid(row=1, column=3, sticky="news")
        self.sbar.grid(row=1, column=4, sticky="news")

        self.lb1.bind("<Button-4>", self.mouse_wheel)
        self.lb1.bind("<Button-5>", self.mouse_wheel)
        self.lb2.bind("<Button-5>", self.mouse_wheel)
        self.lb2.bind("<Button-4>", self.mouse_wheel)

    def scrollbar_change(self, *args) -> None:
        self.lb1.yview(*args)
        self.lb2.yview(*args)

    def mouse_wheel(self, event) -> str:
        direction = 2*event.num-9
        delta = direction
        self.lb1.yview("scroll", delta, "units")
        self.lb2.yview("scroll", delta, "units")
        return "break"

    def insert(self, position, data1: str, data2: str) -> None:
        self.lb1.insert(position, data1)
        self.lb2.insert(position, data2)

    def delete(self, position1, position2) -> None:
        self.lb1.delete(position1, position2)
        self.lb2.delete(position1, position2)

    def clear(self) -> None:
        self.delete("0", "end")

    def yview(self, yview=None) -> None:
        if yview is None:
            return self.lb1.yview()
        self.lb1.yview(yview)
        self.lb2.yview(yview)


class Logger:
    def __init__(self):
        self.old_data = []
        self.new_data = []
        self.paused = False
        self.running = True
        self.blacklisted = []
        self.user_wants_to_see = None
        thread = threading.Thread(target=self.start_up)
        thread.deamon = True
        thread.start()

    def __del__(self) -> None:
        self.close()

    def start_up(self) -> None:
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title("Logger")
        self.root.resizable(False, False)
        self.root.bind("<Control-r>", self.add_blacklist)
        self.b_frame = tk.Frame(self.root)
        self.entry = CustomText(self.root, height=1, width=34)
        self.entry.focus()
        self.button = tk.Button(self.b_frame, text="Clear", command=self.clear)
        self.pbutton = tk.Button(self.b_frame, text="◼", command=self.pause)
        self.listbox = ScrolledListboxes(self.root, width=23)

        self.entry.grid(row=1, column=1, sticky="news")
        self.button.grid(row=1, column=1)
        self.pbutton.grid(row=1, column=2)

        self.b_frame.grid(row=1, column=2, sticky="news")
        self.listbox.grid(row=2, column=1, columnspan=2, sticky="news")

        self.entry.bind("<Escape>", self.delete_input)
        self.entry.bind_modified(self.modified)

        self.mainloop()

    def close(self) -> None:
        self.paused = True
        self.running = False
        self.root.quit()
        self.root.destroy()

    def add_blacklist(self, _) -> None:
        paused = self.paused
        self.paused = True
        self.pbutton["text"] = "▶"

        self.blacklist(self.get_blacklist())
        self.reset()

        self.paused = not paused
        self.pause()

    def blacklist(self, item: str) -> None:
        if item != "":
            self.blacklisted.append(item)

    def get_blacklist(self) -> str:
        window = Question()
        window.ask_user_entry("What do you want to blacklist?")

        kwargs = {"text": "Clear all blacklisted",
                  "command": self.clear_blacklisted}
        window.add_custom(tk.Button, **kwargs)

        window.wait()
        window.destroy()
        return window.result

    def clear_blacklisted(self) -> None:
        self.blacklisted = []

    def pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.pbutton["text"] = "▶"
        else:
            self.pbutton["text"] = "◼"

    def clear(self) -> None:
        self.old_data = []
        self.new_data = []
        self.reset()

    def modified(self, cmd) -> str:
        if (cmd[1] == "insert") and (cmd[3] == "\n"):
            return "break"

    def delete_input(self, _) -> None:
        self.entry.delete("0.0", "end")

    def mainloop(self) -> None:
        while self.running:
            user_wants_to_see = self.entry.get("0.0", "end")
            user_wants_to_see = user_wants_to_see.replace("\n", "")
            self.update_list(user_wants_to_see)
            time.sleep(0.01)
            self.root.update()

    def update_list(self, show_sequence: str) -> None:
        if self.user_wants_to_see == show_sequence:
            self.add_new()
        else:
            self.user_wants_to_see = show_sequence
            self.reset()

    def reset(self) -> None:
        self.listbox.clear()
        self.old_data += self.new_data
        self.new_data = []
        self.add(self.old_data)

    def add(self, _list: list) -> None:
        show_sequence = self.user_wants_to_see
        for sequence, data in _list:
            show = show_sequence in sequence
            for blacklist in self.blacklisted:
                if blacklist in sequence:
                    show = False
            if show:
                self.listbox.insert("end", sequence, data)

    def add_new(self) -> None:
        self.add(self.new_data)
        self.old_data += self.new_data
        self.new_data = []

    def log(self, sequence: str, *args, sep: str=" | ") -> str:
        args = tuple(map(str, args))
        if not self.paused:
            self.new_data.append((str(sequence), sep.join(args)))
        else:
            return "break"

    def kill(self) -> None:
        self.running = False


def _info(text: str, x: int, y :int) -> None:
    root = tk.Tk()
    root.resizable(False, False)
    root.title("Info")
    root.geometry("+%d+%d" % (x, y))
    label = tk.Label(root, text=text)
    button = tk.Button(root, text="Ok", command=root.destroy)
    button.bind("<Return>", lambda e:root.destroy())
    button.focus()
    label.grid(row=1, column=1, sticky="news")
    button.grid(row=2, column=1, sticky="news")
    root.mainloop()

def info(text: str, x: int=None, y: int=None) -> None:
    # The x and the y coordinates that new new window will take
    thread = threading.Thread(target=_info, args=(text, x, y))
    thread.deamon = True
    thread.start()

def askopen(filetypes: tuple, title: str="Select file") -> str:
    filename = askopenfilename(title=title, filetypes=filetypes)
    return filename

def asksave(filetypes: tuple, title: str="Save file") -> str:
    filename = asksaveasfilename(title=title, filetypes=filetypes)
    return filename
