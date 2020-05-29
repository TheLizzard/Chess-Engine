import chess
import re

from position import Position
from .bits import Bits


__all__ = ["compress_move",
           "compress_fen",
           "decompress_move",
           "decompress_fen"]


LETTER_TO_NUMBER = {"p": 0,
                    "n": 1,
                    "b": 2,
                    "r": 3,
                    "q": 4,
                    "k": 5}

NUMBER_TO_LETTER = {v: k for k, v in LETTER_TO_NUMBER.items()}


# Starting compressing move
def get_check_sum(bits_to_sum, bits=None):
    sum = str(bits_to_sum).count("1")
    if bits is not None:
        sum %= bits
    return Bits.from_int(sum, bits=bits)

def compress_move(move):
    position1 = Bits.from_int(move.from_square, bits=6)
    position2 = Bits.from_int(move.to_square, bits=6)
    position = position1.concatenate(position2)

    if move.promotion is None:
        promotion = 0
    else:
        promotion = move.promotion-2
    promotion = Bits.from_int(promotion, bits=2)
    move = position.concatenate(promotion)

    check_sum = get_check_sum(move, bits=2)
    return move.concatenate(check_sum)
# Done compressing move

# Starting decompressing move
def decompress_move(compressed, errors="strict"):
    cpos1, cpos2 = compressed[:6], compressed[6:12]
    cpro, check = compressed[12:14], compressed[14:]
    if str(compressed[:14]).count("1")%len(check) != int(check):
        return "corrupted data"
    pos1 = int(cpos1)
    pos2 = int(cpos2)
    pro = int(cpro)+2
    return chess.Move(pos1, pos2, promotion=pro)
# Done decompressing move

# Starting compressing fen
def _compress_fen(fen):
    result = re.search("(\d+)\/(\d+)", fen)
    if result is not None:
        groups = result.groups()
        number = str(int(groups[0])+int(groups[1]))
        start, end = result.span()
        fen = fen[:start]+_compress_fen(number+fen[end:])
    return fen

def compress_fen(fen):
    fen = _compress_fen(fen).replace("/", "")
    new_fen = Bits()
    i = 0
    while i < len(fen):
        if fen[i].isdigit():
            new = Bits.from_int(0, bits=1)
            if fen[i+1].isdigit():
                number = new.concatenate(Bits.from_int(int(fen[i:i+2]), bits=6))
                new_fen = new_fen.concatenate(number)
                i += 1
            else:
                number = new.concatenate(Bits.from_int(int(fen[i]), bits=6))
                new_fen = new_fen.concatenate(number)
        else:
            new = Bits.from_int(1, bits=1)
            if fen[i] == fen[i].lower():
                new = new.concatenate(Bits.from_int(0, bits=1))
            else:
                new = new.concatenate(Bits.from_int(1, bits=1))
            value = LETTER_TO_NUMBER[fen[i].lower()]
            new = new.concatenate(Bits.from_int(value, bits=3))
            new_fen = new_fen.concatenate(new)
        i += 1
    return new_fen
# Done compressing fen

# Starting decompressing fen
def decompress_fen(bits, errors="strict"):
    fen = ""
    while len(bits) > 0:
        if len(bits) < 5:
            if errors == "strict":
                raise ValueError("Invalid compressed fen")
            else:
                break
        chunk, bits = bits[:5], bits[5:]
        if chunk[0]:
            piece_number = int(chunk[2:])
            piece = NUMBER_TO_LETTER[piece_number]
            if chunk[1]:
                piece = piece.upper()
            fen += piece
        else:
            chunk_part, bits = bits[:2], bits[2:]
            chunk = chunk.concatenate(chunk_part)
            fen += str(int(chunk))
    fen = add_slashes(fen, errors=errors)
    if fen[-1] == "/":
        fen = fen[:-1]
    return fen

def add_slashes(fen, errors="strict"):
    new_fen = ""
    from_last_slash = 0
    i = 0
    while i < len(fen):
        if from_last_slash == 8:
            new_fen += "/"
            from_last_slash = 0
        if fen[i].isdigit():
            if (len(fen) > i+1) and fen[i+1].isdigit():
                number = int(fen[i:i+2])
                i += 1
            else:
                number = int(fen[i])
            while from_last_slash+number >= 8:
                first_part = 8-from_last_slash
                second_part = number-first_part
                new_fen += str(first_part)+"/"
                from_last_slash = 0
                number = second_part
            if number != 0:
                new_fen += str(number)
            from_last_slash += number
        else:
            new_fen += fen[i]
            from_last_slash += 1
        i += 1
    return new_fen
# Done decompressing fen
