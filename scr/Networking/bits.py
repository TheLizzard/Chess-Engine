"""
This module implements the Bits class. It uses a string as its value
(not the best method).
"""


import struct


class Bits:
    def __init__(self, value: str=None):
        if value is None:
            value = ""
        assert isinstance(value, str)
        assert value.replace("1", "").replace("0", "") == ""
        self.value = value

    def __repr__(self) -> str:
        if self.value == "":
            value = "None"
        else:
            value = self.value
        return "<Bits object at "+hex(id(self))+" value="+value+">"

    def __getitem__(self, key) -> str:
        return Bits(self.value[key])

    def __bool__(self) -> bool:
        return (self.value != "0") and (self.value != "")

    def __int__(self) -> int:
        return self.to_int()

    def __bytes__(self) -> bytes:
        return self.to_bytes()

    def __str__(self) -> str:
        return self.value

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Can't add Bits object with: "+repr(other))
        return Bits.from_int(int(self)+int(other))

    def __xor__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Can't xor Bits object with: "+repr(other))
        return Bits.from_int(int(self)^int(other))

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Can't subtract Bits object with: "+repr(other))
        return Bits.from_int(int(self)-int(other))

    def __mul__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Can't multiply Bits object with: "+repr(other))
        return Bits.from_int(int(self)*int(other))

    def __len__(self) -> int:
        return len(self.value)

    def to_int(self) -> int:
        if self.value == "":
            return 0
        return int(self.value, 2)

    def to_bytes(self, errors="strict") -> bytes:
        if (len(self)%8 != 0):
            if errors == "strict":
                raise ValueError("bits not a multiple of 8")
            else:
                self = self.concatenate(Bits("0"*(8-len(self)%8)))
        
        output = bytes()
        for i in range(int(len(self)/8)):
            chunk = int(self[i*8:(i+1)*8])
            output += struct.pack("!B", chunk)
        return output

    def concatenate(self, other):
        return Bits(self.value+other.value)

    @classmethod
    def from_bytes(cls, _bytes: bytes):
        bits = cls()
        for i in _bytes:
            bits = bits.concatenate(cls.from_int(i, bits=8))
        return bits

    @classmethod
    def from_int(cls, value: int, bits=None):
        if not isinstance(value, int):
            raise ValueError("value must be an int.")
        output = "{0:b}".format(value)
        if bits is not None:
            if bits-len(output) < 0:
                raise ValueError("Can't fit the value in that number of bits.")
            output = "0"*(bits-len(output))+output
        return cls(output)
