import copy
import os
import re


BLOCK_REGEX = " *\t*(\w+):(\n[\t ]+.+)*"
LINE_REGEX = "\"([^\n=]+)\" *(= *([^\n=]+))*"
TUPLE_REGEX = "\((([\w\". -]*?),* *)+\)"
TUPLE_REGEX = "\((([\w. \"]+),* *)+\)"


DEFAULT_SETTINGS = """Menu:
    "tearoff" = False
    "File" = ("Open", "Save", "Save as", "-----", "Exit")
    "Edit" = ("Undo Move", "Redo Move", "-----", "Change Position")
    "View" = ("Current FEN", "Game PGN")
    "Game" = ("Evaluate", "-", "Play vs Computer", "Play vs Human", "Play vs AI", "Play Multiplayer")
    "Settings" = ("Game Settings", "Suggested Moves Settings")
    "Help" = ("Licence", "Help")

widgets:
    "borderwidth" = 0
    "highlightthickness" = 0
    "justify" = "left"

GameBoard:
    "size_of_squares" = 60
    "dark_squares" = "grey"
    "light_squares" = "white"
    "chess_pieces_set_number" = 2
    "scale_for_pieces" = 1.4
    "font" = ("", 9)
    "last_move_colour_white" = "#DDDDDD"
    "last_move_colour_black" = "#555555"
    "arrow_colour" = "light green"
    "arrow_width" = 5
    "ring_colour" = "light green"
    "ring_width" = 4
    "ring_radius" = 27
    "available_moves_dots_colour" = "black"

Root:
    "background" = "grey"

Evaluation:
    "width" = 160
    "height" = 45
    "colour" = "white"
    "background" = "grey"
    "font" = ("Lucida Console", 20)
    "stockfish" = "Stockfish/stockfish_10_x64"

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
    "font" = ("Lucida Console", 10)"""



class Setting:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = Setting(**value)
            self.__dict__.update({key: value})

    def __repr__(self):
        output = "<Setting object at "+str(hex(id(self)))
        output += " "+str(self.__dict__)+">"
        return output

    def __str__(self):
        return str(self.__dict__)

    def __getitem__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise IndexError("Couldn't find the index: "+str(key)+"in",
                             " this class.")

    def pop(self, *args, **kwargs):
        return self.__dict__.pop(*args, **kwargs)

    def items(self, *args, **kwargs):
        return self.__dict__.items(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def deepcopy(self):
        return copy.deepcopy(self)

    def dict(self):
        return self.__dict__


class Settings:
    def __init__(self, file="settings.ini"):
        if os.path.exists(file):
            with open(file, "r") as file:
                data = file.read()
            self.settings = self.parse(data)
            self.set_settings(self.settings)
        else:
            print("Couldn't read the settings file so using the default ones.")
            self.settings = self.parse(DEFAULT_SETTINGS)
            self.set_settings(self.settings)

    def parse(self, data):
        return parse(data)

    def set_settings(self, settings):
        for setting in settings:
            setting = self.lower_case_key(setting)
            for key, value in setting.items():
                self.__dict__.update({key: Setting(**value)})

    def lower_case_key(self, setting):
        if isinstance(setting, dict):
            output = {}
            for key, value in setting.items():
                output.update({key.lower(): self.lower_case_key(value)})
            return output
        else:
            return setting

    def reset(self, file="settings.ini"):
        with open(file, "w") as file:
            file.write(DEFAULT_SETTINGS)

    def update(self):pass


def parse(line):
    if line.count(" ") == len(line):
        return "break"
    result = re.finditer(BLOCK_REGEX, line)
    result = tuple(map(group, result))
    if len(result) > 0:
        result = tuple(map(parse_block, result))
        return result

    result_match = re.search(LINE_REGEX, line)
    if result_match is not None:
        result = result_match.groups()
        if (len(result) == 3) and (result[2] is not None):
            key, _, value = result
            return {key: parse_value(value)}
        elif (len(result) == 3) and (result[1] == result[2] is None):
            key, _, _ = result
            return key


def parse_value(value):
    if value.isdigit():  #check if integer
        return int(value)

    if check_if_float(value):  #check if float
        return float(value)

    if string_to_bool(value) is not None:  #check if boolean
        return string_to_bool(value)

    if check_if_tuple(value) is not None:  #check if tuple
        return check_if_tuple(value)

    if value[0] == value[-1] == "\"":  #check if string
        return value[1:][:-1]


def check_if_float(string):
    has_max_one_dot = string.replace(".", "", 1).isdigit()
    dot_not_at_end = string[-1] != "."
    return has_max_one_dot and dot_not_at_end

def check_if_tuple(string):
    if (string[0] == "(") and (string[-1] == ")"):
        result = string[1:][:-1].split(", ")
        output = []
        for substring in result:
            output.extend(substring.split(","))
        output = tuple(map(parse_value, output))
        return output

def string_to_bool(string):
    if string.lower() in ("y", "yes", "t", "true", "on"):
        return True
    if string.lower() in ("n", "no", "f", "false", "off"):
        return False

def group(reMatch):
    return reMatch.group()

def parse_block(block):
    result = re.search(BLOCK_REGEX, block)
    if result is not None:
        name = result.group(1)
        block = block.replace(name+":\n", "")
        result = {}
        for line in block.split("\n"):
            parsed_line = parse(line)
            if parsed_line != "break":
                result.update(parsed_line)
        return {name: result}


"""
BLOCK_REGEX = " *\t*(\w+):(\n[\t ]+.+)*"
LINE_REGEX = "\"([^\n=]+)\" *(= *([^\n=]+))*"
TUPLE_REGEX = "\((.*?), *(.*?)\)"
"""
