import discord

import Games.game as game
from Games.print import Print

class Game_Print():
    def __init__(self):
        self.game = game.Game()
        self.deck_look = Print(Print.CLASSIC)
        self.hand_messages = [] #Variable to hold most recent hand message for each player. leave blank 
        self.end = []
        self.commands = {
            "^!join$": [self.join],
            "^!jion$": [self.join],
            "^!unjoin$": [self.unjoin],
            "^!unjion$": [self.unjoin],
            "^!start$": [self.start],
            "^!end$": [self.end_game],
            "^!classic$": [self.change_look, self.change_look_parse],
            "^!genshin$": [self.change_look, self.change_look_parse],
            "^!starwars$": [self.change_look, self.change_look_parse]
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
                    return self.add_return([], f"Welcome to the game, {player.name}! Type **!start** to begin game with {len(self.game.get_players())} players.")
                else:
                    return self.add_return([], f"Sorry, {player.name}. This game already has 8 players {[player.name for player in self.game.get_players()]}.")
            else:
                return self.add_return([], f"You've already queued for this game, {player.name}. Type **!start** to begin game with {len(self.game.get_players())} players.")
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
                    self.end.append(False)
                    self.hand_messages.append(None)
                return self.add_return([], f"Game started by {str(player)}.\n{self.get_start_string(player)}")
            else:
                return self.add_return([], "Something went wrong when starting the game.")
        else:
            return self.add_return([], f"You can't start a game you aren't queued for, {player.name}. Use **!join** to join the game.")
        
    #Input: player and str as defined in message.py for commands
    #Output: add_return print for message handler
    async def end_game(self, player):
        return_list = []

        if player in self.game.get_players():
            #If end list (game started) initiated
            if (len(self.end) > 0) and (self.game.game_started):
                self.end[self.game.get_players().index(player)] = True
                self.add_return(return_list, f"{player.name} has voted to end the game early. Use **!end** to agree. Must be unanimous.")
                
                #If everyone has voted, end game
                if self.end.count(True) == len(self.end):
                    self.add_return(return_list, f"Game has been ended early.\n{self.get_end_string(player)}")
            else:
                self.add_return(return_list, f"You can't end a game that hasn't started yet, {player.name}.")
        else:
            self.add_return(return_list, f"You're not in the game, {player.name}.")

        return return_list
    
    def change_look_parse(self, parse_str):
        if parse_str == "!genshin":
            return [Print.GENSHIN]
        elif parse_str == "!starwars":
            return [Print.STARWARS]
        else:
            return [Print.CLASSIC]
    
    async def change_look(self, player, look):
        if player in self.game.get_players():
            self.deck_look = Print(look)
            return self.add_return([], f"Appearance of deck has been changed to {look}! Use **!start** to try it out!")
        else:
            return self.add_return([], f"You can't edit a game you aren't queued for, {player.name}. Use **!join** to join the game.")
        
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
                hand_pic = self.deck_look.get_hand_pic([self.game.get_hand(player)])
                await self.hand_messages[self.game.get_player_index(player)].edit_original_response(attachments=[discord.File(fp=hand_pic, filename="HandPic.png")])

    #Deletes a player's hand display if applicable. Does nothing if no hand is displayed in discord
    async def delete_last_hand(self, player, replacement=None):
        if player in self.game.get_players():
            if self.hand_messages[self.game.get_player_index(player)] != None:
                await self.hand_messages[self.game.get_player_index(player)].delete_original_response()
            self.hand_messages[self.game.get_player_index(player)] = replacement
    
    #Returns the hand image if applicable, or None
    def get_hand_pic(self, player, show_index:bool=True):
        if player in self.game.get_players():
            hand = self.game.get_hand(player)
            if hand != None:
                return self.deck_look.get_hand_pic([hand], show_index)
        
        return None
###############################################################################
# List of common functions that may be implemented
###############################################################################
    #Returns the string to be displayed when the game is started
    def get_start_string(self, player) -> str:
        return ""
    
    #Returns the string to be displayed when the game is ended
    def get_end_string(self, player) -> str:
        return ""