import chess.engine

import settings


settings = settings.Settings()
STOCKFISH_LACATION = settings.evaluation.stockfish
del settings


class Analyse:
    def __init__(self, board):
        self.board = board
        self.running = True
        self.score = None
        self.moves = None

    def start(self):
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_LACATION)

        with engine.analysis(self.board) as analysis:
            for info in analysis:
                self.score = info.get("score")
                self.moves = info.get("pv")

                if not self.running:
                    break
        engine.quit()

    def stop(self):
        self.running = False

    def kill(self):
        self.running = False
