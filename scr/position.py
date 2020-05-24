#https://codegolf.stackexchange.com/questions/63772/determine-the-color-of-a-chess-square
import chess

from settings import Settings


SIZE = Settings().gameboard.size_of_squares


class Move:
    def __init__(self, position1, position2):
        self.position1 = position1
        self.position2 = position2

    def to_str(self):
        place1 = self.position1.to_place()
        place2 = self.position2.to_place()
        return place1 + place2

    def __hash__(self):
        string = str(self.position1.to_int())+str(self.position2.to_int())
        return int(string)


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other): #returns a Move object
        if isinstance(other, self.__class__):
            return Move(self, other)
        else:
            raise ValueError(repr(other)+"has to be an instance"\
                             " of: "+self.__class__.__name__)

    def __mul__(self, other): #returns a Move object
        if isinstance(other, int):
            return Move(self, self)
        else:
            raise ValueError(repr(other)+"has to be an instance of: <int>")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.x == other.x:
                if self.y == other.y:
                    return True
        return False

    def __ne__(self, other): # easier to port to python 2 in the future
        return not (self == other)

    def __repr__(self):
        out = "<Position object at "+hex(id(self))
        out += " x="+str(self.x)+" y="+str(self.y)+">"
        return out

    def __getitem__(self, key):
        if isinstance(key, int):
            if key == 0:
                return self.x
            elif key == 1:
                return self.y
            else:
                raise IndexError("Key must be eather 0 or 1"\
                                 "for x or y not "+str(key))

    def to_coords(self):
        x = (self.x-0.5)*SIZE
        y = (8.5-self.y)*SIZE
        return (self.round(x), self.round(y))

    def to_coords_start(self):
        x = (self.x-1)*SIZE
        y = (8-self.y)*SIZE
        return (self.round(x), self.round(y))

    def to_coords_end(self):
        x = (self.x)*SIZE
        y = (9-self.y)*SIZE
        return (self.round(x), self.round(y))

    def to_place(self):
        return chess.FILE_NAMES[self.x-1]+str(self.y)

    def to_int(self):
        return 8*self.y+self.x-9

    def to_colour(self):
        return int(self.to_place(), 35)%2 # Converts to base 35 first.

    @staticmethod
    def round(x):
        return int(x+0.5)

    @classmethod
    def from_coords(cls, coords):
        x, y = coords
        new_x = x//SIZE+1
        new_y = (SIZE*8-y)//SIZE+1
        return cls(Position.round(new_x), Position.round(new_y))

    @classmethod
    def from_int(cls, _int):
        x = _int%8+1
        y = _int//8+1
        return cls(x, y)
