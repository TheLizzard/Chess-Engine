from PIL import Image, ImageTk
import tkinter as tk


SPRITES_LOCATION = "Sprites/"


class Piece:
    def __init__(self, name, position, colour, settings, master):
        self.name = name
        self.colour = colour
        self.master = master
        self.tkcanvasnum = None
        self.position = position
        self.settings = settings
        self.sqr_size = settings.size_of_squares
        self.set = settings.chess_pieces_set_number
        self.filename = self.get_filename(name=name, colour=colour,
                                          set=self.set)
        self.image = self.get_image(filename=self.filename)
        self.size = self.image.size

    def get_image(self, filename):
        return Image.open(filename)

    def get_filename(self, name, colour, set):
        filename = SPRITES_LOCATION+"set."+str(set)+"/"+name+"."+colour+".png"
        return filename

    def place(self, pos):
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.tkcanvasnum = self.master.create_image(pos, image=self.tkimage)

    def show(self, position=None):
        if position is None:
            x, y = self.position
        else:
            x, y = position
        x_pix = (x-0.5)*(self.sqr_size)-2
        y_pix = (8.5-y)*(self.sqr_size)-2
        pos = (x_pix, y_pix)
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.tkcanvasnum = self.master.create_image(pos, image=self.tkimage)

    def destroy(self):
        if self.tkcanvasnum is not None:
            self.master.delete(self.tkcanvasnum)

    def resize(self, scale=None, height=None, width=None):
        if scale is not None:
            if (height is not None) or (width is not None):
                raise ValueError("Can't specify the scale with the (height or width)")
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

    def resize_max(self, max_height, max_width):
        self.resize(max_height)
        self.resize(max_width)

    def _resize(self):
        size = tuple(map(lambda x:int(x+0.5), self.size))
        self.image = self.image.resize(size, 0)  # 0 for Image.NEAREST

    def resize_scale(self, scale):
        self.size = tuple(map(lambda x:x*scale, self.size))
        self._resize()
