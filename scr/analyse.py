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

    def start(self) -> None:
        """
        This is a very simple engine to get the best move and the current
        score by using Stockfish. This implementation uses a endless loop.
        """
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_LACATION)

        with engine.analysis(self.board) as analysis:
            for info in analysis:
                self.score = info.get("score")
                self.moves = info.get("pv")

                if not self.running:
                    break
        engine.quit()

    def stop(self) -> None:
        self.running = False

    def kill(self) -> None:
        self.running = False
