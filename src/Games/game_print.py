import Games.game as game
from Games.Prints.default_print import Default_Print

class game_print():
    def __init__(self):
        self.game = game.Game()
        self.deck_print = Default_Print()
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
        if(self.game.game_started == False):
            #Add person to player list and send confirmation message
            if(player not in self.game.players):
                if(len(self.game.players) < 8):
                    self.game.players.append(player)
                    return self.add_return([], f"Welcome to the game, {player.name}! Type !start to begin game with {len(self.game.players)} players.")
                else:
                    return self.add_return([], f"Sorry, {player.name}. This game already has 8 players {[player.name for player in self.game.players]}. If this is wrong, type !unjoinall.")
            else:
                return self.add_return([], f"You've already queued for this game, {player.name}. Type !start to begin game with {len(self.game.players)} players.")
        return []

    def unjoin(self, player):
        if(self.game.game_started == False):
            #Remove person from player list and send confirmation message
            if(player in self.game.players):
                self.game.players.remove(player)
                return self.add_return([], f"So long, {player.name}.")
            else:
                return self.add_return([], f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        return []

    def start(self, player):
        if player in self.game.players:
            if self.game.start_game():
                return self.add_return([], "Game started by " + str(player))
            else:
                return self.add_return([], "Something went wrong when starting the game.")
        else:
            return self.add_return([], f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        
    #Get list of players in game
    def get_players(self):
        return self.game.players
    
###############################################################################
# Implement below functions as needed
###############################################################################
    #Creates teams based on the team_count, the player, and 
    def create_teams(self, player, team_count:int):
        return self.add_return([], "Teams not implemented for this game.")