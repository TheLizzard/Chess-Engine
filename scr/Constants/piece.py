from PIL import Image, ImageTk
import tkinter as tk

from .SuperClass import SuperClass
from .settings import Settings
from .position import Position

SETTINGS = Settings().gameboard
SPRITES_LOCATION = "Sprites/"


class Piece(SuperClass):
    def __init__(self, name: str, position: Position, colour: bool,
                 master: tk.Canvas):
        self.name = name
        self.colour = colour
        self.master = master
        self.tkcanvasnum = None
        self.position = position
        self.sqr_size = SETTINGS.size_of_squares
        filename = self.get_filename(name, colour,
                                     SETTINGS.chess_pieces_set_number)
        self.image = Image.open(filename)
        self.size = self.image.size

    def get_filename(self, name: str, colour: bool, set: int) -> str:
        """
        Gets the filename for the sprite file based on the name, colour,
        and set number
        """
        if colour:
            colour = "white"
        else:
            colour = "black"
        return SPRITES_LOCATION+"set."+str(set)+"/"+name+"."+colour+".png"

    def place(self, coords: tuple) -> None:
        """
        Displays the piece on the tkinter canvas at `coords` where `coords`
        is a tuple of tkinter canvas coords
        """
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.tkcanvasnum = self.master.create_image(coords, image=self.tkimage)

    def show(self) -> None:
        """
        Shows the sprite on the screen where `self.position` is.
        """
        x, y = self.position
        # Centre the image in the square:
        pos = ((x-0.5)*self.sqr_size, (8.5-y)*self.sqr_size)
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.tkcanvasnum = self.master.create_image(pos, image=self.tkimage)

    def destroy(self) -> None:
        """
        Removes the sprite from the screen.
        """
        # Make sure that the sprite is actually on the screen
        if self.tkcanvasnum is not None:
            self.master.delete(self.tkcanvasnum)

    def resize(self, scale=None, height=None, width=None) -> None:
        """
        The main resize function
        You need to give it a scale or (height and width).
        """
        if scale is not None:
            # The scale is given
            # Make sure that the height and width aren't given:
            if (height is not None) or (width is not None):
                raise ValueError("Can't specify the scale with the (height" \
                                 " or width)")
            # Resize accordingly
            self.resize_scale(scale=scale)
            return None
        elif (height is None) and (width is None):
            # Nothing is given so letts ignore the call to this method
            return None
        elif height is None:
            # Only the width is given
            w, h = self.size
            self.size = (width, width*h/w)
        elif width is None:
            # Only the height is given
            w, h = self.size
            self.size = (height*w/h, height)
        else:
            # Both the width and height are given
            self.size = (width, height)
        self._resize()

    def _resize(self) -> None:
        """
        Applies all resizing changes to the sprite.
        Note it rounds all of the sizes
        """
        # Round the size to the nearest int:
        size = (int(self.size[0]+0.5), int(self.size[1]+0.5))
        self.image = self.image.resize(size, Image.NEAREST)

    def resize_scale(self, scale: float) -> None:
        """
        Resizes the sprite based on the scale that it is given.
        """
        self.size = (self.size[0]*scale, self.size[1]*scale)
        self._resize()
