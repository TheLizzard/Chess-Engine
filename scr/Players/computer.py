"""
This implements the Computer class. It uses Stockfish to calculate a move
from a board position when go is called.
"""


from chess.engine import SimpleEngine, Limit, Mate

from .player import Player


"""
Get the correct Stockfish file that the OS can use. Fix for Issue #20.
    stockfish_11_x64      # For Linux 64 bit
    stockfish_11_x32.exe  # For Windows 32 bit
    stockfish_11_x64.exe  # For Windows 64 bit
"""
import settings
# Get the folder of all of the Sockfishes
STOCKFISH_FOLDER = settings.Settings().evaluation.stockfish
os_bits = str(settings.get_os_bits()) # Get the bit version of the OS
# Get the file extension that the OS supports
os_extension = settings.get_os_extension()
# Combine everything to get the location
STOCKFISH_LACATION = STOCKFISH_FOLDER+os_bits+os_extension
del settings, os_bits, os_extension, STOCKFISH_FOLDER # clean up


class Computer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def go(self) -> None:
        # We don't want any errors because the game is over or we lost
        # permissions to send moves to GUIBoard
        if (self.board.is_game_over()) or (not self.alowed_to_play):
            return None
        # Improvement: Add a changing depth and time
        self.limit = Limit(depth=DEPTH, time=TIME)
        with SimpleEngine.popen_uci(STOCKFISH_LOCATION) as engine:
            result = engine.play(self.board, self.limit)
        self.callback(result.move)
