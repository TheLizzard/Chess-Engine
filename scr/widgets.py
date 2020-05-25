import tkinter as tk


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
