#https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
from functools import partial
from tkinter import ttk
import tkinter as tk
import threading
import time
import re


class TextWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_attributes("-type", "splash")
        self.text = tk.Text(self.root)
        self.sbar = tk.Scrollbar(self.root, command=self.text.yview)
        self.button = tk.Button(self.root, text="Ok", command=self.root.destroy)
        self.text.config(yscrollcommand=self.sbar.set)
        self.text.grid(row=1, column=1, sticky="news")
        self.sbar.grid(row=1, column=2, sticky="news")
        self.button.grid(row=2, column=1, columnspan=2, sticky="news")
        self.disable()

    def disable(self):
        self.text.config(state="disabled")

    def enable(self):
        self.text.config(state="normal")

    def insert(self, *args):
        if self.text["state"] == "disabled":
            self.enable()
        self.text.insert(*args)
        if self.text["state"] == "disabled":
            self.disable()


class CopyableWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_attributes("-type", "splash")
        self.button_c = tk.Button(self.root, text="Copy", command=self.copy)
        self.button = tk.Button(self.root, text="Ok", command=self.root.destroy)
        self.button_c.grid(row=1, column=2, sticky="news")
        self.button.grid(row=2, column=1, columnspan=2, sticky="news")

    def add_widget(self, widget):
        self.widget = widget
        self.widget.grid(row=1, column=1, sticky="news")

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.get())
        self.root.update()


class CopyableEntryWindow(CopyableWindow):
    def __init__(self):
        super().__init__()
        self.text = tk.Entry(self.root)
        super().add_widget(self.text)

    def set(self, string):
        self.widget.insert(0, string)

    def clear(self):
        self.widget.delete(0, "end")

    def get(self):
        return self.widget.get()


class CopyableTextWindow(CopyableWindow):
    def __init__(self):
        super().__init__()
        self.text = tk.Text(self.root)
        super().add_widget(self.text)

    def set(self, string):
        self.text.insert("0.0", string)

    def clear(self):
        self.text.delete("0.0", "end")

    def get(self):
        return self.text.get("0.0", "end")


class AutoScrollbar(tk.Scrollbar):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry_manager_kwargs = {}
        self.text_widget = text_widget
        self.geometry_manager = None
        self.hidden = True

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
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
        super().set(lo, hi)

    def pack(self, **kwargs):
        super().pack(**kwargs)
        self.geometry_manager = "pack"
        self.geometry_manager_kwargs = kwargs

    def place(self, **kwargs):
        super().place(**kwargs)
        self.geometry_manager = "place"
        self.geometry_manager_kwargs = kwargs

    def grid(self, **kwargs):
        super().grid(**kwargs)
        self.geometry_manager = "grid"
        self.geometry_manager_kwargs = kwargs


class LicenceWindow(TextWindow):
    def __init__(self):
        super().__init__()
        self.insert("end", self.get_text())

    def get_text(self):
        with open("Licence.txt", "r") as file:
            data = file.read()
        return data


class HelpWindow(TextWindow):
    def __init__(self):
        super().__init__()
        self.insert("end", self.get_text())

    def get_text(self):
        with open("Help.txt", "r") as file:
            data = file.read()
        return data


class Tk(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.binds = []
        super().__init__(*args, **kwargs)

    def bind_update(self, func):
        self.binds.append(func)

    def update(self, *args, **kwargs):
        for func in self.binds:
            func()
        super().update(*args, **kwargs)


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

        return self.tk.call(cmd)

    def generate_event(self, cmd):
        for bind in self.binds:
            if bind(cmd) == "break":
                return "break"

    def bind_modified(self, function):
        self.binds.append(function)

    def unbind_modified(self, function):
        if self.binds.count(function) > 0:
            self.binds.remove(function)

    def paste(self, event):
        if len(self.tag_ranges("sel")) != 0:
            self.delete("sel.first", "sel.last")

    def select_all(self, event):
        self.tag_add("sel", "0.0", "end")
        self.mark_set("insert", "end")


class Question:
    def __init__(self):
        self.result = None
        self.root = Tk()
        self.root.resizable(False, False)

    def destroy(self):
        self.root.destroy()

    def get(self):
        return self.result

    def wait(self):
        while self.result is None:
            time.sleep(0.01)
            self.root.update()

    def add_custom(self, cls, *args, **kwargs):
        widget = cls(self.root, *args, **kwargs)
        widget.grid(column=1, columnspan=10, sticky="news")

    def ask_for_ip(self):
        font = ("Lucida Console", 18)
        kwargs = {"borderwidth": 0, "highlightthickness": 0}

        text = "What IP do you want to connect to?"
        self.label = tk.Label(self.root, text=text, **kwargs)
        self.label.grid(row=1, column=1, columnspan=2, sticky="news")

        self.entry = CustomText(self.root, height=1, width=15, font=font,
                                **kwargs)
        self.entry.grid(row=2, column=1)
        self.entry.bind_modified(self.check_ip)

        self.button = tk.Button(self.root, text="Done",
                                command=self._ask_for_ip, **kwargs)
        self.button.grid(row=2, column=2, sticky="news")

    def _ask_for_ip(self):
        if self.check_ip():
            self.result = self.entry.get("0.0", "end").replace("\n", "")

    def check_ip(self, event=None):
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
        else:
            self.entry.config(bg="light green")
            return True

    def ask_user_multichoice(self, question, answers, mapping=None):
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

    def _ask_user_multichoice(self, event):
        self.result = event

    def ask_user_entry(self, question):
        commmand = self._ask_user_entry
        self.root.bind("<Return>", commmand)
        self.label = tk.Label(self.root, text=question)
        self.entry = tk.Entry(self.root)
        self.button = tk.Button(self.root, text="Done", command=commmand)

        self.label.grid(row=1, column=1, columnspan=2, sticky="news")
        self.entry.grid(row=2, column=1, sticky="news")
        self.button.grid(row=2, column=2, sticky="news")

    def _ask_user_entry(self, event=None):
        self.result = self.entry.get()


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

    def scrollbar_change(self, *args):
        self.lb1.yview(*args)
        self.lb2.yview(*args)

    def mouse_wheel(self, event):
        direction = 2*event.num-9
        delta = direction
        self.lb1.yview("scroll", delta, "units")
        self.lb2.yview("scroll", delta, "units")
        return "break"

    def insert(self, position, data1, data2):
        self.lb1.insert(position, data1)
        self.lb2.insert(position, data2)

    def delete(self, position1, position2):
        self.lb1.delete(position1, position2)
        self.lb2.delete(position1, position2)

    def clear(self):
        self.delete("0", "end")

    def yview(self, yview=None):
        if yview is None:
            return self.lb1.yview()
        self.lb1.yview(yview)
        self.lb2.yview(yview)


class Logger:
    def __init__(self):
        self.old_data = []
        self.new_data = []
        self.running = True
        self.paused = False
        self.blacklisted = []
        self.user_wants_to_see = None
        thread = threading.Thread(target=self.start_up)
        thread.deamon = True
        thread.start()

    def start_up(self):
        self.root = tk.Tk()
        self.root.title("Logger")
        self.root.resizable(False, False)
        self.root.bind("<Control-r>", self.add_blacklist)
        self.b_frame = tk.Frame(self.root)
        self.entry = CustomText(self.root, height=1, width=34)
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

    def add_blacklist(self, event):
        paused = self.paused
        self.paused = True
        self.pbutton["text"] = "▶"

        self.blacklist(self.get_blacklist())
        self.reset()

        self.paused = not paused
        self.pause()

    def blacklist(self, item):
        if item != "":
            self.blacklisted.append(item)

    def get_blacklist(self):
        window = Question()
        window.ask_user_entry("What do you want to blacklist?")

        kwargs = {"text": "Clear all blacklisted",
                  "command": self.clear_blacklisted}
        window.add_custom(tk.Button, **kwargs)

        window.wait()
        window.destroy()
        return window.result

    def clear_blacklisted(self):
        self.blacklisted = []

    def pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pbutton["text"] = "▶"
        else:
            self.pbutton["text"] = "◼"

    def clear(self):
        self.old_data = []
        self.new_data = []
        self.reset()

    def modified(self, cmd):
        if (cmd[1] == "insert") and (cmd[3] == "\n"):
            return "break"

    def delete_input(self, event):
        self.entry.delete("0.0", "end")

    def mainloop(self):
        while self.running:
            user_wants_to_see = self.entry.get("0.0", "end")
            user_wants_to_see = user_wants_to_see.replace("\n", "")
            self.update_list(user_wants_to_see)
            time.sleep(0.01)
            self.root.update()

    def update_list(self, show_sequence):
        if self.user_wants_to_see == show_sequence:
            self.add_new()
        else:
            self.user_wants_to_see = show_sequence
            self.reset()

    def reset(self):
        self.listbox.clear()
        self.old_data += self.new_data
        self.new_data = []
        self.add(self.old_data)

    def add(self, _list):
        show_sequence = self.user_wants_to_see
        for sequence, data in _list:
            show = show_sequence in sequence
            for blacklist in self.blacklisted:
                if blacklist in sequence:
                    show = False
            if show:
                self.listbox.insert("end", sequence, data)

    def add_new(self):
        self.add(self.new_data)
        self.old_data += self.new_data
        self.new_data = []

    def log(self, sequence, *args, sep=" | "):
        args = tuple(map(str, args))
        if not self.paused:
            self.new_data.append((str(sequence), sep.join(args)))
        else:
            return "break"

    def kill(self):
        self.running = False


if __name__ == "__main__":
    """
    a = Question()
    print(a.ask_for_ip())
    a.destroy()

    a = Question()
    print(a.ask_user("Do you want?", ("y", "n"), (True, False)))
    a.destroy()
    """
    l = Logger()
    for i in range(20):
        l.log("connection.recv.heartbeat")
