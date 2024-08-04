import Backend.game as game

class game_print():
    def __init__(self):
        self.game = game.Game()
        self.commands = {
            "^!join$": [self.join],
            "^!jion$": [self.join],
            "^!unjoin$": [self.unjoin],
            "^!unjion$": [self.unjoin],
            "^!start$": [self.start]
        }

    def add_return(self, return_list, return_string, file=None, index=None):
        if(index == None):
            index = len(return_list)

        if(index >= len(return_list)):
            return_list.append([return_string, file])
        elif(index < len(return_list)):
            return_list.insert(index, [return_string, file])

        return return_list

    def join(self, player):
        self.game.add_player(player)

    def unjoin(self, player):
        self.game.remove_player(player)

    def start(self, player):
        if self.game.start_game():
            return self.add_return([], "Game started by " + str(player))
        else:
            return self.add_return([], "Something went wrong when starting the game.")