import discord
from random import randint, shuffle
import re

from Games.game_print import Game_Print
from Games.Juiced.juiced_print import Juiced_Print
from Games.Cribbage.cribbage_print import Cribbage_Print

class Test_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        self.game_print:Game_Print = Juiced_Print()
        self.game_name = "Juiced"
        self.players = []
        
        #Add commands
        self.commands = {
            "^!start$": [self.start],
            "^!end$": [self.end_game],
            "^!join$": [self.explain_rules],
            "^!jion$": [self.explain_rules],
        }
        self.commands["^!cribbage$"] = [self.make_cribbage]
        self.commands["^!cr$"] = [self.make_cribbage]
        self.commands["^!juiced$"] = [self.make_juiced]
        self.commands["^!jc$"] = [self.make_juiced]
        self.commands["^!add .*$"] = [self.add_player]

    async def explain_rules(self, _player):
        return self.add_return([], "Use '!add *player*' to add a player to the game.")
    
    # OVERRIDE #
    async def change_look(self, player, look):
        return self.game_print.change_look(player, look)
        
    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self, player) -> str:
        return f"Test of {self.game_name} has been started.\n{self.game_print.get_start_string(player)}"
    
    # OVERRIDE #
    #Returns the string to be displayed when the game is ended
    def get_end_string(self, player) -> str:
        return f"Test has been ended\n{self.game_print.get_end_string(player)}"
    
    #Used as a dummy function to "delete" a command
    def null_command(self, player):
        return []
    
    #Adds Cribbage game
    async def make_cribbage(self, _player):
        if not self.game_print.is_started():
            self.game_print = Cribbage_Print()
            self.game_name = "Cribbage"
            self.HAND_PIC = self.game_print.HAND_PIC
            return self.add_return([], "Game has been changed to Cribbage. Use **!start** to begin.")
        
        return self.add_return([], "Failed to change game since game has been started. Use **!end** to end.")
    
    #Adds Juiced game
    async def make_juiced(self, _player):
        if not self.game_print.is_started():
            self.game_print = Juiced_Print()
            self.game_name = "Juiced"
            self.HAND_PIC = self.game_print.HAND_PIC
            return self.add_return([], "Game has been changed to Juiced. Use **!start** to begin.")
        
        return self.add_return([], "Failed to change game since game has been started. Use **!end** to end.")
    
    #Parses the string for self.add_player
    def add_player_parse(self, parse_str:str):
        return parse_str.split(sep=" ", maxsplit=1)[1]

    #Adds a player to the game
    async def add_player(self, player, message):
        new_player = self.add_player_parse(message)
        if (not self.game_print.is_started()) and (self.game_print.game.add_player(new_player) == True):
            #Add player to players for message.py
            if player not in self.players:
                self.players.append(player)

            #Add command for new player and return
            self.commands[f"^!{new_player} .*$"] = [self.handle_command, self.handle_command_parse]
            more_players = self.game_print.game.min_player_count-len(self.game_print.get_players())
            return self.add_return([], f"Added {new_player} to the game! Use '!{new_player} *command*' to play as them, and '!{new_player} hand' to print their hand.\n{more_players if more_players>0 else "No"} more player(s) are needed to start the game.")
        
        return self.add_return([], f"Failed to add player to the game.")
    
    #Parses the command for self.handle_command
    def handle_command_parse(self, parse_str:str):
        output_list = parse_str.split(sep=" ", maxsplit=1)
        output_list[0] = output_list[0][1:]
        return output_list
    
    #Handles commands passed in from the player to pass on to the underlying game
    async def handle_command(self, _actual_player, player, message):
        if player in self.game_print.game.get_players():
            #If they want the hand, give it to them
            if message == "hand":
                if self.game_print.HAND_PIC == False:
                    return self.add_return([], self.game_print.get_hand_string(player))
                else:
                    return self.add_return([], f"{player}'s hand:", self.game_print.get_hand_pic(player))
                
            #If they don't want the hand, return whatever they asked for
            return await self.run_commands(player, message, self.game_print)
        
        #if invalid, return empty list for message.py
        return []

    #Runs the command if needed or returns empty list
    async def run_commands(self, player, message, game:Game_Print):
        for command in game.commands:
            if re.fullmatch(command, message) != None:
                func_list = game.commands[command]
                if len(func_list) > 1:
                    return await func_list[0](player, *(func_list[1](message)))
                else:
                    return await func_list[0](player)
                    
        return []
    
    #Returns the hand image if applicable, or None
    def get_hand_pic(self, player, show_index:bool=True):
        if player in self.game_print.game.get_players():
            hand = self.game_print.game.get_hand(player)
            if hand != None:
                return self.game_print.deck_look.get_hand_pic([hand], show_index)
        
        return None
    
    #Returns the hand string
    def get_hand_string(self, player):
        return self.game_print.get_hand_string(player)

    #Starts the game
    async def start(self, player):
        if self.game_print.game.start_game():
            #Initialize local vars
            for _ in self.game_print.game.get_players():
                self.game_print.end.append(False)
                self.game_print.hand_messages.append(None)
            return self.add_return([], f"Game started by {str(player)}.\n{self.get_start_string(player)}")
        else:
            return self.add_return([], "Something went wrong when starting the game.")
        
    #Input: player and str as defined in message.py for commands
    #Output: add_return print for message handler
    async def end_game(self, player):
        self.game_print.game.end_game()
        return self.add_return([], f"Game has been ended early.\n{self.get_end_string(player)}")
        
    #Get list of players in game
    def get_players(self):
        return self.players
    
    #Returns True if game is started (running), or False if game is not active
    def is_started(self) -> bool:
        return self.game_print.game.game_started
    
    #Updates a player's hand if applicable. Does nothing if get_hnd_pic isn't defined
    async def update_hand(self, player):
        if player in self.game_print.game.get_players():
            if self.HAND_PIC == True:
                if self.game_print.hand_messages[self.game_print.game.get_player_index(player)] != None:
                    hand_pic = self.deck_look.get_hand_pic([self.game_print.game.get_hand(player)])
                    await self.game_print.hand_messages[self.game_print.game.get_player_index(player)].edit_original_response(attachments=[discord.File(fp=hand_pic, filename="HandPic.png")])
            else:
                if self.game_print.hand_messages[self.game_print.game.get_player_index(player)] != None:
                    hand_str = self.get_hand_string(player)
                    await self.game_print.hand_messages[self.game_print.game.get_player_index(player)].edit_original_response(content=hand_str)

    #Deletes a player's hand display if applicable. Does nothing if no hand is displayed in discord
    async def delete_last_hand(self, player, replacement=None):
        if player in self.game_print.game.get_players():
            if self.game_print.hand_messages[self.game_print.game.get_player_index(player)] != None:
                await self.game_print.hand_messages[self.game_print.game.get_player_index(player)].delete_original_response()
            self.game_print.hand_messages[self.game_print.game.get_player_index(player)] = replacement