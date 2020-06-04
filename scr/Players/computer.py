from chess.engine import SimpleEngine, Limit, Mate

from .player import Player
import settings

settings = settings.Settings()
STOCKFISH_LOCATION = settings.evaluation.stockfish
DEPTH = settings["gameboard.computer"].depth
TIME = settings["gameboard.computer"].time
del settings


class Computer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def go(self):
        if (self.board.is_game_over()) or (not self.alowed_to_play):
            return None
        self.limit = Limit(depth=DEPTH, time=TIME)
        with SimpleEngine.popen_uci(STOCKFISH_LOCATION) as engine:
            result = engine.play(self.board, self.limit)
        self.callback(result.move)
