import requests
import re
import os


BASE = "https://raw.githubusercontent.com/TheLizzard/Chess-Engine/master/scr/"


def download() -> None:
    # get the files need to be updated
    # We need to add a progress bar for the user to see
    files_to_download = get_files()
    length = len(files_to_download)
    for i, file in enumerate(files_to_download):
        print("Downloading file: "+file+"\t\t file "+str(i+1)+"/"+str(length))
        download_file(file)
    print("updating the record")
    download_file("files.txt")

def get_files() -> tuple:
    response = requests.get(BASE+"files.txt").text
    return parse_files(response)

def download_file(file_name: str):
    os.makedirs(os.path.dirname("Chess-Engine/"+file_name), exist_ok=True)
    with open("Chess-Engine/"+file_name, "wb") as file:
        file.write(requests.get(BASE+file_name).content)

def parse_files(text: str) -> dict:
    text += "\n" # add a blank line for the re.findall step
    text = re.sub(" *#[^\n]+\n", "\n", text) # remove comments
    result = re.findall("([^\n ]+?) +([\d.]+?)\n", text)  # find the file|date
    return dict(result) # make it into a dictionary


if __name__ == "__main__":
    download()
