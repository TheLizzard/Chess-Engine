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


from Constants.SuperClass import SuperClass
import chess.engine
import threading


"""
Get the correct Stockfish file that the OS can use. Fix for Issue #20.
    stockfish_11_x64      # For Linux 64 bit
    stockfish_11_x32.exe  # For Windows 32 bit
    stockfish_11_x64.exe  # For Windows 64 bit
"""
import Constants.settings as settings
# Get the folder of all of the Sockfishes
STOCKFISH_FOLDER = settings.Settings().evaluation.stockfish
os_bits = str(settings.get_os_bits()) # Get the bit version of the OS
# Get the file extension that the OS supports
os_extension = settings.get_os_extension()
# Combine everything to get the location
STOCKFISH_LACATION = STOCKFISH_FOLDER+os_bits+os_extension
del settings, os_bits, os_extension, STOCKFISH_FOLDER # clean up


class Analyse(SuperClass):
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

                new_score = info.get("score")
                if new_score is not None:
                    self.score = new_score

                new_moves = info.get("pv")
                if new_moves is not None:
                    self.moves = new_moves

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
