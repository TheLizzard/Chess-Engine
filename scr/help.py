import tkinter as tk


class Help:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_attributes("-type", "splash")
        self.text = tk.Text(self.root)
        self.sbar = tk.Scrollbar(self.root, command=self.text.yview)
        self.button = tk.Button(self.root, text="Ok", command=self.root.destroy)
        self.text.insert("end", self.get_text())
        self.text.config(state="disabled", yscrollcommand=self.sbar.set)
        self.text.grid(row=1, column=1, sticky="news")
        self.sbar.grid(row=1, column=2, sticky="news")
        self.button.grid(row=2, column=1, columnspan=2, sticky="news")

    def get_text(self):
        with open("Help.txt", "r") as file:
            data = file.read()
        return data
