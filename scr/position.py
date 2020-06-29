#https://codegolf.stackexchange.com/questions/63772/determine-the-color-of-a-chess-square

"""
This module is the core of the whole program. This does all
of the calculations between different ways of saying chess position.
For example all of these are the same place (assuming the size
of a square = 60):
    as a place         A8
    as an int          56
    as x and y         1, 8
    as coords          (30, 30)
    as coords (start)  (0, 0)
    as coords (end)    (60, 60)

This library is called a lot of times so it is very important to
keep it as fast and clean as possible.
"""

import chess

from settings import Settings


SIZE = Settings().gameboard.size_of_squares


class Move:
    def __init__(self, position1, position2):
        self.position1 = position1
        self.position2 = position2

    def to_str(self) -> str:
        return self.position1.to_place() + self.position2.to_place()

    def __hash__(self) -> int:
        return int(str(self.position1.to_int())+str(self.position2.to_int()))


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other) -> Move:
        if isinstance(other, self.__class__):
            return Move(self, other)
        else:
            raise ValueError(repr(other)+" has to be an instance"\
                             " of: "+self.__class__.__name__)

    def __mul__(self, other) -> Move:
        if isinstance(other, int):
            return Move(self, self)
        else:
            raise ValueError(repr(other)+"has to be an instance of: <int>")

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (self.x == other.x)\
               and (self.y == other.y)

    def __repr__(self) -> str:
        return f"<Position object at {hex(id(self))} x={self.x} y={self.y}>"

    def __getitem__(self, key: int) -> int:
        if isinstance(key, int):
            if key == 0:
                return self.x
            elif key == 1:
                return self.y
            else:
                raise IndexError("Key must be eather 0 or 1"\
                                 "for x or y not "+str(key))

    def __int__(self) -> int:
        return self.to_int()

    def to_coords(self) -> tuple:
        return (int((self.x-0.5)*SIZE+0.5), int((8.5-self.y)*SIZE+0.5))

    def to_coords_start(self) -> tuple:
        return (int((self.x-1)*SIZE+0.5), int((8-self.y)*SIZE+0.5))

    def to_coords_end(self) -> tuple:
        return (int((self.x)*SIZE+0.5), int((9-self.y)*SIZE+0.5))

    def to_place(self) -> str:
        return chess.FILE_NAMES[self.x-1]+str(self.y)

    def to_int(self) -> int:
        return 8*self.y+self.x-9

    def to_colour(self) -> bool:
        return bool(int(self.to_place(), 35)%2) # Converts to base 35 first.

    @classmethod
    def from_coords(cls, coords: tuple):
        x, y = coords
        return cls(int(x//SIZE+1+0.5), int((SIZE*8-y)//SIZE+1+0.5))

    @classmethod
    def from_int(cls, _int: int):
        return cls(_int%8+1, _int//8+1)
