#https://stackoverflow.com/questions/1405913/how-do-i-determine-if-my-python-shell-is-executing-in-32bit-or-64bit-mode-on-os
from SuperClass import SuperClass
import platform
import struct
import copy
import os
import re

BLOCK_REGEX = "([^:\n]+):( *#[^\n]*){0,1}(\n[ \t]+[^\n]*)+"
LINE_REGEX = "\"(.*?)\" *= *(.+)"
TUPLE_REGEX = "\((([\w. \"]+),* *)+\)"


class Setting(SuperClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = Setting(**value)
            self.__dict__.update({key: value})

    def __str__(self) -> str:
        return str(self.__dict__)

    def __getitem__(self, key: str):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise IndexError("Couldn't find the index: "+str(key)+" in" \
                             " this class.")

    def pop(self, idx=None):
        return self.__dict__.pop(idx)

    def items(self):
        return self.__dict__.items()

    def update(self, dictionary: dict) -> None:
        self.__dict__.update(dictionary)

    def deepcopy(self):
        return copy.deepcopy(self)

    def dict(self) -> dict:
        return self.__dict__


class Settings(SuperClass):
    def __init__(self, file="settings.ini"):
        self.update()

    def __getitem__(self, key: str) -> Setting:
        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise IndexError("Couldn't find the index: "+str(key)+" in" \
                             " this class.")

    def parse(self, data: str) -> dict:
        return parse(data)

    def set_settings(self, settings: dict) -> None:
        settings = self.lower_case_key(settings)
        for key, value in settings.items():
            if isinstance(value, dict):
                value = Setting(**value)
            self.__dict__.update({key: value})

    def lower_case_key(self, setting: dict) -> dict:
        if isinstance(setting, dict):
            output = {}
            for key, value in setting.items():
                output.update({key.lower(): self.lower_case_key(value)})
            return output
        else:
            return setting

    def reset(self, file="settings.ini") -> None:
        """
        Resets to the default settings.
        """
        with open(file, "w") as file:
            file.write(DEFAULT_SETTINGS)

    def update(self, file="settings.ini") -> None:
        """
        Reads the settings from the file if it exists.
        """
        if os.path.exists(file):
            with open(file, "r") as file:
                data = file.read()
            settings = self.parse(data)
        else:
            print("Couldn't read the settings file so using the default ones.")
            settings = self.parse(DEFAULT_SETTINGS)
        self.set_settings(settings)


def parse(data: str) -> dict:
    output = {}
    result = re.finditer(BLOCK_REGEX, data)

    if result is not None:
        for block in result:
            block = block.group()
            output.update(parse_block(block))
            data = data.replace(block, "", 1)

    for line in data.split("\n"):
        output.update(parse_line(line))

    return output

def parse_line(line: str) -> dict:
    """Returns a dict of the parsed line or None"""

    line = line.lstrip()
    # check if the line is empty or a comment
    if (line == "") or (line[0] == "#"):
        return {}

    result = re.search(LINE_REGEX, line)
    if result is not None:
        result = result.groups()
        if len(result) == 2:
            key, value = result
            return {key: parse_value(value)}
    raise ValueError("Can't parse this line: "+line)

def parse_value(value: str):
    if value == "None": # check if the value is None
        return None

    if value.isdigit():  #check if the value is int
        return int(value)

    if check_if_float(value):  #check if the value is float
        return float(value)

    if string_to_bool(value) is not None:  #check if the value is bool
        return string_to_bool(value)

    if check_if_tuple(value) is not None:  #check if the value is tuple
        return check_if_tuple(value)

    if value[0] == value[-1] == "\"":  #check if the value is str
        return value[1:][:-1]

    raise ValueError("The value is not a valid type: "+value)


def check_if_float(string: str) -> bool:
    has_max_one_dot = string.replace(".", "", 1).isdigit()
    dot_not_at_end = string[-1] != "."
    return has_max_one_dot and dot_not_at_end

def check_if_tuple(string: str):
    if (string[0] == "(") and (string[-1] == ")"):
        result = string[1:][:-1].split(", ")
        output = []
        for substring in result:
            output.extend(substring.split(","))
        output = tuple(map(parse_value, output))
        return output
    return None

def string_to_bool(string: str) -> bool:
    if string.lower() in ("y", "yes", "t", "true", "on"):
        return True
    if string.lower() in ("n", "no", "f", "false", "off"):
        return False
    return None

def parse_block(block: str) -> dict:
    result = re.search(BLOCK_REGEX, block)
    if result is not None:
        name = result.group(1)
        block = block.split("\n", 1)[1]
        result = {}
        for line in block.split("\n"):
            parsed_line = parse_line(line)
            result.update(parsed_line)
        return {name: result}
    raise ValueError("Can't parse this block: "+block)

def get_os_bits() -> int:
    return 8 * struct.calcsize("P")

def get_os_extension() -> int:
    os = platform.system()
    if os.lower() == "windows":
        return ".exe"
    elif os.lower() == "linux":
        return ""
    else:
        raise OSError("Can't recognise the OS type.")


DEFAULT_SETTINGS = """
# This is a file that contains all of the settings
# There 6 types allowed:
#      --------- ---------------------------- -----------------
#     | Type    | Example value 1            | Example value 2 |
#      --------- ---------------------------- -----------------
#     | boolean | True                       | False           |
#     | string  | "Hello world"              | "this is a str" |
#     | integer | 1                          | 5               |
#     | None    | None                       | None            |
#     | float   | 1.02                       | 3.14159         |
#     | tuple   | ("values", 1, True, False) | (0.0, None)     |
#      --------- ---------------------------- -----------------
#


"report_errors" = True
"update" = True


Menu:
    "tearoff" = False
    "File" = ("Open", "Save", "Save as", "-----", "Exit")
    "Edit" = ("Undo Move", "Redo Move", "-----", "Change Position")
    "View" = ("Current FEN", "Game PGN")
    "Game" = ("Evaluate", "-", "Play vs Computer", "Play vs Human", "Play vs AI", "Play Multiplayer")
    "Settings" = ("Game Settings", "Board Settings")
    "Help" = ("Licence", "Help")

Widgets:
    "borderwidth" = 0
    "highlightthickness" = 0

GameBoard:
    "size_of_squares" = 60
    "dark_squares" = "grey"
    "light_squares" = "white"
    "chess_pieces_set_number" = 2
    "scale_for_pieces" = 1.4
    "last_move_colour_white" = "#BBBBBB"
    "last_move_colour_black" = "#666666"

GameBoard.User: # Same for multiplayer as well
    "arrow_colour" = "light green"
    "arrow_width" = 5
    "ring_colour" = "light green"
    "ring_width" = 4
    "ring_radius" = 27
    "available_moves_dots_colour" = "black"

GameBoard.Computer:
    "depth" = None
    # In seconds
    "time" = 2

Root:
    "background" = "grey"

Evaluation:
    "width" = 160
    "height" = 45
    "colour" = "white"
    "background" = "grey"
    "font" = ("Lucida Console", 20)
    "stockfish" = "Stockfish/stockfish_11_x"

SuggestedMoves:
    "colour" = "white"
    "background" = "grey"
    "font" = ("Lucida Console", 10)

MoveHistory:
    "width" = 160
    "height" = 380
    "line_width" = 19
    "line_height" = 30
    "auto_hide_scrollbar" = True
    "colour" = "white"
    "background" = "grey"
    "cursor_colour" = "white"
    "font" = ("Lucida Console", 10)
"""


REGEXES_BACKUP = {
    "BLOCK_REGEX": "([^:\n]+):( *#[^\n]*){0,1}(\n[ \t]+[^\n]*)+",
    "LINE_REGEX": "\"(.*?)\" *= *(.+)",
    "TUPLE_REGEX": "\((([\w. \"]+),* *)+\)"}
