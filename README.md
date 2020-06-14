# Chess-Engine
This is a simple GUI chess engine for Linux based systems (not Windows).


## Supported Operating systems
Currently only 1 operating system is supported: Ubuntu. The program should run on any Linux system but I can't test it.
#### Note: The program doesn't run on Windows at all (I am trying to fix that).


## Dependencies
Currently there is only 1 dependancy (python-chess).
On `Linux` do: `pip3 install python-chess`


## How to run:
Run using `python 3` run `scr/main.py`.


## Errors
If you get this error: `PermissionError: [Errno 13] Permission denied: 'Stockfish/stockfish_10_x64'` than you need to set the Execute bit on Sockfish to be 1. To do that follow these instuctions: https://askubuntu.com/a/485001/1002358.


## Bugs
If you get any bugs or unexpected behaviors please report it to https://github.com/TheLizzard/Chess-Engine/issues.
