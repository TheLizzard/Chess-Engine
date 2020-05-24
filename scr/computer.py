from player import Player
from chess.engine import SimpleEngine, Limit, Mate


class Computer(Player):
    def __init__(self, board, colour, guiboard, depth=None, time=2,
                 callback=None):
        self.callback = callback
        self.guiboard = guiboard
        super().__init__(board=board, colour=colour)
        self.limit = Limit(depth=depth, time=time)

    def go(self):
        if (self.board.is_game_over()) or (not self.alowed_to_play):
            return None
        with SimpleEngine.popen_uci("Stockfish/stockfish_10_x64") as engine:
            result = engine.play(self.board, self.limit)
        move = result.move
        self.guiboard.push(move)
        if self.callback is not None:
            self.callback()
