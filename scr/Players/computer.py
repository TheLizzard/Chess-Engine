from chess.engine import SimpleEngine, Limit, Mate

from .player import Player
import settings

settings = settings.Settings()
STOCKFISH_LOCATION = settings.evaluation.stockfish
del settings


class Computer(Player):
    def __init__(self, board, colour, depth=None, time=2, callback=None):
        self.callback = callback
        self.depth = depth
        self.time = time
        super().__init__(board=board, colour=colour)

    def go(self):
        if (self.board.is_game_over()) or (not self.alowed_to_play):
            return None
        self.limit = Limit(depth=self.depth, time=self.time)
        with SimpleEngine.popen_uci(STOCKFISH_LOCATION) as engine:
            result = engine.play(self.board, self.limit)
        move = result.move
        if self.callback is not None:
            self.callback(move)
        else:
            return move
