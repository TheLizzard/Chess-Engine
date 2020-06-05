"""
This is a very simple engine to get the best move and the current
score by using Stockfish. This implementation uses a endless loop.
Use:
    import time

    analyses = Analyse(chess.Board())
    analyses.start()

    for i in range(30):
        if (analyses.score is not None) and (analyses.moves is not None):
            print("Score:", analyses.score, "\tBest move:", analyses.moves[0])
        time.sleep(0.1)

    analyses.stop()
"""


import chess.engine
import threading

import settings


settings = settings.Settings()
STOCKFISH_LACATION = settings.evaluation.stockfish
del settings


class Analyse:
    def __init__(self, board: chess.Board):
        self.board = board
        self.running = True
        self.score = None
        self.moves = None

    def start(self) -> None:
        """
        This calls the `mainloop` method in a separate thread. Use
        Analyse.score to get the score and Analyse.moves to get the
        next best moves.
        """
        thread = threading.Thread(target=self.mainloop)
        thread.deamon = True
        thread.start()

    def mainloop(self) -> None:
        """
        This is the `mainloop`. It shouldn't be called inside the main thread
        as it will take over the thread forever unless something calls
        the `stop` method. Use the `start` method. It creates a separate
        thread for the mainloop.
        This loop runs until the `running` attribute is False.
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
        """
        This stops the mainloop by setting the `running` attribute to False.
        """
        self.running = False

    def kill(self) -> None:
        """
        This stops the mainloop by setting the `running` attribute to False.
        """
        self.running = False
