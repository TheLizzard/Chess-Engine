import requests
import re
import os


BASE = "https://raw.githubusercontent.com/TheLizzard/Chess-Engine/master/scr/"


def update() -> bool:
    # get the files need to be updated
    # We need to add a progress bar for the user to see
    files_to_update = check_for_update()
    length = len(files_to_update)
    for i, file in enumerate(files_to_update):
        print("updating file: "+file+"\t\t file "+str(i)+"/"+str(length))
        update_file(file)
    if len(files_to_update) > 0:
        print("updating the record")
        update_file("files.txt")

def check_for_update() -> tuple:
    with open("files.txt", "r") as file:
        current = file.read()
    try:
        response = requests.get(BASE+"files.txt").text
        new = parse_files(response)
        current = parse_files(current)
        return difference_dicts(current, new)
    except:
        return tuple()

def update_file(file_name: str):
    if os.path.dirname(file_name) != "":
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
    try:
        data = requests.get(BASE+file_name)
    except:
        print("Couldn't update file: "+file_name)
        return None
    with open(file_name, "wb") as file:
        file.write(data.content)

def parse_files(text: str) -> dict:
    text += "\n" # add a blank line for the re.findall step
    text = re.sub(" *#[^\n]+\n", "\n", text) # remove comments
    result = re.findall("([^\n ]+?) +([\d.]+?)\n", text)  # find the file|date
    return dict(result) # make it into a dictionary

def difference_dicts(old, new) -> tuple:
    output = []
    old_keys = old.keys()
    for key, new_value in new.items():
        if (key not in old_keys) or (new_value != old[key]):
            output.append(key)
    return tuple(output) # need to add a way to remove unused files
