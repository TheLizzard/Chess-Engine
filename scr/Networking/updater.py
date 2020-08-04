import requests
import re


LOCATION = "https://raw.githubusercontent.com/TheLizzard/Chess-Engine/master/"


def update() -> bool:
    files_to_update = check_for_update() # get the files need to be updated
    for file in files_to_update:
        update_file(file)
    return (len(files_to_update) > 0)

def check_for_update() -> tuple:
    with open("files.txt", "r") as file:
        current = file.read()
    response = requests.get(LOCATION+"files.txt").text

    new = parse_files(response)
    current = parse_files(current)

    return difference_dicts(current, new)

def update_file(file: str):
    with open(file, "w") as file:
        file.write(requests.get(LOCATION+file).text)


def parse_files(text: str) -> dict:
    text += "\n" # add a blank line for the re.findall step
    text = text.replace("\n\n", "\n") # remove blank lines
    text = re.sub("#[^\n]+\n", "", text) # remove comments
    result = re.findall("([^\n ]+?) +([^\n ]+?)\n", text) # find the file|date
    return dict(result) # make it into a dictionary

def difference_dicts(old, new) -> tuple:
    output = []
    old_keys = old.keys()
    for key, new_value in new.items():
        if key in old_keys:
            if not (new_value == old[key]):
                output.append(key)
    return tuple(output) # need to add a way to remove unused files
