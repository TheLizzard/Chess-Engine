from PIL import Image, ImageTk
import tkinter as tk

from settings import Settings
from position import Position

SETTINGS = Settings().gameboard
SPRITES_LOCATION = "Sprites/"


class Piece:
    def __init__(self, name: str, position: Position, colour: bool,
                 master: tk.Canvas):
        self.name = name
        self.colour = colour
        self.master = master
        self.tkcanvasnum = None
        self.position = position
        self.sqr_size = SETTINGS.size_of_squares
        self.set = SETTINGS.chess_pieces_set_number
        filename = self.get_filename(name=name, colour=colour, set=self.set)
        self.image = Image.open(filename)
        self.size = self.image.size

    def get_filename(self, name: str, colour: bool, set: int) -> str:
        if colour:
            colour = "white"
        else:
            colour = "black"
        filename = SPRITES_LOCATION+"set."+str(set)+"/"+name+"."+colour+".png"
        return filename

    def place(self, coords: tuple) -> None:
        """
        Displays the piece on the tkinter canvas at `coords` where `coords`
        is a tuple of tkinter canvas coords
        """
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.tkcanvasnum = self.master.create_image(coords, image=self.tkimage)

    def show(self, position: tuple=None) -> None:
        if position is None:
            x, y = self.position
        else:
            x, y = position
        size = self.sqr_size
        x_pix = (x-0.5)*size
        y_pix = (8.5-y)*size
        pos = (x_pix, y_pix)
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.tkcanvasnum = self.master.create_image(pos, image=self.tkimage)

    def destroy(self) -> None:
        if self.tkcanvasnum is not None:
            self.master.delete(self.tkcanvasnum)

    def resize(self, scale=None, height=None, width=None) -> None:
        if scale is not None:
            if (height is not None) or (width is not None):
                raise ValueError("Can't specify the scale with the (height" \
                                 " or width)")
            else:
                self.resize_scale(scale=scale)
            return None
        elif (height is None) and (width is None):
            return None
        elif height is None:
            w, h = self.size
            self.size = (width, width*h/w)
        elif width is None:
            w, h = self.size
            self.size = (height*w/h, height)
        else:
            self.size = (width, height)
        self._resize()

    def resize_max(self, max_height, max_width) -> None:
        self.resize(max_height)
        self.resize(max_width)

    def _resize(self) -> None:
        size = (int(self.size[0]+0.5), int(self.size[1]+0.5))
        self.image = self.image.resize(size, Image.NEAREST)

    def resize_scale(self, scale) -> None:
        self.size = (self.size[0]*scale, self.size[1]*scale)
        self._resize()
