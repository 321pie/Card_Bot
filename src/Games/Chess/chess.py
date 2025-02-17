import Games.game as game

class Chess(game.Game):
    def __init__(self):
        super().__init__()
        self.req_players:int = 2

    def initialize_game(self) -> bool:
        match len(self.players):
            case _ if len(self.players) < self.req_players:
                return False
            case _ if len(self.players) > 4:
                return False
            case 3:
                return False
        return True

    def move(self, pos_a, pos_b) -> str:
        return "hi"

