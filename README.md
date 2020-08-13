# Chess-Engine
This is a simple GUI chess engine for Linux and Windows.

## Dependencies:
There are 2 dependancies:
* python-chess:
  * On `Windows` do: `python -m pip install python-chess`
  * On `Linux` do: `pip3 install python-chess`
* PIL/Pillow:
  * On `Windows` do: `python -m pip install pillow`
  * On `Linux` do: `pip3 install pillow; sudo apt-get install python3-pil python3-pil.imagetk`

## How to download:
Download the <a href=https://github.com/TheLizzard/Chess-Engine-Downloader>downloader</a> and run `downloader.py` using `python 3`. It will download all of the nessasary files with their updates.

## How to run:
Using `python 3` run `scr/main.py`.

## Errors:
If you get this error: `PermissionError: [Errno 13] Permission denied: 'Stockfish/stockfish_11_x64'` than you need to set the Execute bit on Sockfish to be 1. To do that follow these instuctions: https://askubuntu.com/a/485001/1002358.

## Bugs:
If you get any bugs or unexpected behaviors please report it to https://github.com/TheLizzard/Chess-Engine/issues.
