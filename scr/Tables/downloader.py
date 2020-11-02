import urllib.request
from re import findall
from os.path import isfile

def download_webpage(webpage):
    htmlfile = urllib.request.urlopen(webpage)
    htmltext = htmlfile.read()
    return htmltext

def search_for_patterm(text, pattern):
    return findall(pattern, text)


folder = "syzygy/"
website = r"https://tablebase.lichess.ovh/tables/standard/3-4-5/"
pattern = r"\w+.rtbz"# rtbw

data = str(download_webpage(website))
_list = search_for_patterm(data, pattern)


for counter, filename in enumerate(_list):
    downloadpath = website + filename
    print(str(int(counter/len(_list)*10000)/100)+"%")
    if not isfile(folder+filename):
        try:
            data = download_webpage(downloadpath)
            with open(folder+filename, "wb") as file:
                file.write(data)
        except MemoryError:
            with open("ERRORS.txt", "a") as error:
                error.write(str(filename)+"\n")
                print(filename)

#145
