#https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
from functools import partial
import tkinter as tk
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
        self.root = Tk()
        self.root.resizable(False, False)

    def destroy(self):
        self.root.destroy()

    def ask_for_ip(self):
        self.result = None
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

        while self.result is None:
            self.root.update()

        return self.result

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

    def ask_user(self, question, answers, mapping=None):
        self.result = None
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
            cmd = partial(self._ask_user, event)
            button = tk.Button(self.root, text=answer, command=cmd)
            button.grid(row=2, column=i+1, sticky="news")
            self.buttons.append(button)

        while self.result is None:
            self.root.update()

        return self.result

    def _ask_user(self, event):
        self.result = event


if __name__ == "__main__":
    a = Question()
    print(a.ask_for_ip())
    a.destroy()

    a = Question()
    print(a.ask_user("Do you want?", ("y", "n"), (True, False)))
    a.destroy()
