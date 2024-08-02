import Backend.game as game

class game_print():
    def __init__(self):
        self.game = game.Game()
        self.commands = {
            "^!join$": self.join,
            "^!jion$": self.join,
            "^!unjoin$": self.unjoin,
            "^!unjion$": self.unjoin,
            "^!start$": self.start,
            "^![0-9]+$": [self.select_card, self.select_card_parse]
        }