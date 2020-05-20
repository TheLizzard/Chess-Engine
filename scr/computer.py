from player import Player
from chess.engine import SimpleEngine, Limit, Mate


class Computer(Player):
    def __init__(self, board, colour, depth=None, time=2):
        self.time = time
        self.depth = depth
        super().__init__(board=board, colour=colour)
        self.limit = Limit(depth=self.depth, time=self.time)

    def go(self):
        if (self.board.is_game_over()) or (not alowed_to_play):
            return None
        with SimpleEngine.popen_uci("Stockfish/stockfish_10_x64") as engine:
            result = engine.play(self.board, self.limit)
        move = result.move
        self.board.push(move)
