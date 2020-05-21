import widgets


class Help(widgets.TextWindow):
    def __init__(self):
        super().__init__()
        self.insert("end", self.get_text())

    def get_text(self):
        with open("Help.txt", "r") as file:
            data = file.read()
        return data
