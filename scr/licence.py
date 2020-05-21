import widgets


class Licence(widgets.TextWindow):
    def __init__(self):
        super().__init__()
        self.insert("end", self.get_text())

    def get_text(self):
        with open("Licence.txt", "r") as file:
            data = file.read()
        return data
