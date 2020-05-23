class Player:
    def __init__(self, board, colour):
        self.board = board
        self.alowed_to_play = False
        self.colour = self.colour_to_bool(colour)

    def colour_to_bool(self, colour):
        if isinstance(colour, str):
            if colour == "white":
                return True
            elif colour == "black":
                return False
        elif isinstance(colour, bool):
            return colour
        elif isinstance(colour, int) and ((0 == colour) or (1 == colour)):
            return colour

    def start(self):
        self.alowed_to_play = True

    def stop(self):
        self.alowed_to_play = False

    def destroy(self):
        self.stop()
