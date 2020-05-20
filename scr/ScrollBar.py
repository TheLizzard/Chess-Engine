import tkinter as tk


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

#raise tk.TclError("Cannot use **** manager with this widget")
