import requests
import re


BASE = "https://raw.githubusercontent.com/TheLizzard/Chess-Engine/master/"
LOCATION = BASE+"scr/"


def update() -> bool:
    # get the files need to be updated
    files_to_update, record = check_for_update()
    for file in files_to_update:
        update_file(file)
    if len(files_to_update) > 0:
        update_record(record)
        return True
    return False

def check_for_update() -> tuple:
    with open("files.txt", "r") as file:
        current = file.read()
    response = requests.get(BASE+"files.txt").text

    new = parse_files(response)
    current = parse_files(current)

    return difference_dicts(current, new), response

def update_file(file_name: str):
    with open(file_name, "wb") as file:
        file.write(requests.get(LOCATION+file_name).content)

def update_record(record: str) -> None:
    with open("files.txt", "w") as file:
        file.write(record)


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
        if (key not in old_keys) or (new_value != old[key]):
            output.append(key)
    return tuple(output) # need to add a way to remove unused files
