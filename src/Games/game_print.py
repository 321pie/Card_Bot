import discord

import Games.game as game
from Games.print import Print

class Game_Print():
    def __init__(self):
        self.game = game.Game()
        self.deck_look = Print(Print.CLASSIC)
        self.hand_messages = [] #Variable to hold most recent hand message for each player. leave blank 
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

    async def join(self, player):
        if(self.game.game_started == False):
            #Add person to player list and send confirmation message
            if(player not in self.game.get_players()):
                if(len(self.game.get_players()) < self.game.max_player_count):
                    self.game.add_player(player)
                    return self.add_return([], f"Welcome to the game, {player.name}! Type !start to begin game with {len(self.game.get_players())} players.")
                else:
                    return self.add_return([], f"Sorry, {player.name}. This game already has 8 players {[player.name for player in self.game.get_players()]}. If this is wrong, type !unjoinall.")
            else:
                return self.add_return([], f"You've already queued for this game, {player.name}. Type !start to begin game with {len(self.game.get_players())} players.")
        return []

    async def unjoin(self, player):
        if(self.game.game_started == False):
            #Remove person from player list and send confirmation message
            if(player in self.game.get_players()):
                self.game.remove_player(player)
                return self.add_return([], f"So long, {player.name}.")
            else:
                return self.add_return([], f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        return []

    async def start(self, player):
        if player in self.game.get_players():
            if self.game.start_game():
                #Initialize local vars
                for _ in self.game.get_players():
                    self.hand_messages.append(None)
                return self.add_return([], "Game started by " + str(player))
            else:
                return self.add_return([], "Something went wrong when starting the game.")
        else:
            return self.add_return([], f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        
    #Get list of players in game
    def get_players(self):
        return self.game.get_players()
    
    #Returns True if game is started (running), or False if game is not active
    def is_started(self) -> bool:
        return self.game.game_started
    
    #Updates a player's hand if applicable. Does nothing if get_hnd_pic isn't defined
    async def update_hand(self, player):
        if player in self.game.get_players():
            if self.hand_messages[self.game.get_player_index(player)] != None:
                hand_pic = await self.deck_look.get_hand_pic(self.game.get_hand(player))
                await self.hand_messages[self.game.get_player_index(player)].edit_original_response(attachments=[discord.File(hand_pic)])

    #Deletes a player's hand display if applicable. Does nothing if no hand is displayed in discord
    async def delete_last_hand(self, player, replacement=None):
        if player in self.game.get_players():
            if self.hand_messages[self.game.get_player_index(player)] != None:
                await self.hand_messages[self.game.get_player_index(player)].delete_original_response()
            self.hand_messages[self.game.get_player_index(player)] = replacement
    
###############################################################################
# List of common functions that may be implemented
###############################################################################
    #Returns the hand image if applicable, or None
    async def get_hand_pic(self, player, show_index:bool=True):
        return None