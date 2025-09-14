from random import randint, shuffle

from Games.game_print import Game_Print
from Games.Wavelength.wavelength import Wavelength
import Games.Wavelength.wavelength_deck as wd

class Wavelength_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        super().__init__()

        self.deck_look = None
        self.game = Wavelength()
        self.scrambled_unholy_actions:list[list] = []
        
        #Add commands
        self.commands["^!all$"] = [self.all]
        self.commands["^!defualt$"] = [self.default]
        self.commands["^!base$"] = [self.base]
        self.commands["^!coders$"] = [self.coders]
        self.commands["^!goal [0-9]+$"] = [self.change_goal]
        self.commands["^!guess -?([0-9]|(10))$"] = [self.make_long_guess]
        self.commands["^!g -?([0-9]|(10))$"] = [self.make_short_guess]
    
    # OVERRIDE #
    async def change_look(self, player, _look):
        if player in self.game.get_players():
            return self.add_return([], f"Feature not available for this game. Sorry! <3")
        else:
            return self.add_return([], f"You can't edit a game you aren't a part of, {player}. Use **!join** to join an unstarted game.")
        
    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self, _player) -> str:
        return f"**{self.game.get_judge()}** is the judge. The category is:\n**{self.get_card_string(self.game.get_judge_card())}**\nPlease make a guess between {self.game.lowest_guess} and {self.game.highest_guess} based on the hint by using the **!guess** command.\nJudges use **/h** or **/hand** to see the correct answer and give your hint."
    
    # OVERRIDE #
    #Returns the string to be displayed when the game is ended
    def get_end_string(self, _player) -> str:
        return f"The game has been ended early.\n{self.get_point_string()}\nThe winner is: **{self.game.get_winner(True)}**"

    #Returns a string that has a list each player and their corresponding point totals
    def get_point_string(self):
        output_string = "**Total Points:**\n"
        for player in self.game.get_players():
            output_string += f"*{player}*: {self.game.get_points(player)}\n"

        return output_string

    #Returns the string from a hand
    def get_card_string(self, card:wd.dk.Card):
        return card.value
    
    #Gets the "hand" (AKA the correct answer for the judge)
    def get_hand_string(self, player):
        if player in self.game.get_players():
            if player == self.game.get_judge():
                return str(self.game.correct_answer)
            else:
                return f"You need to guess between {self.game.lowest_guess} and {self.game.highest_guess} based on the hint by using the **!guess** command."
        else:
            return f"You aren't in the game {player}, so you don't have a hand."
        
    #Used to parse the "!guess " off the message
    async def make_long_guess(self, player, message):
        guess = int(message[7:])
        return self.make_guess(player, guess)
    
    #Used to parse the "!g " off the message
    async def make_short_guess(self, player, message):
        guess = int(message[3:])
        return self.make_guess(player, guess)

    #Used to make a guess (requires parse for guess from message)
    def make_guess(self, player, guess):
        output_list = []
        round_ended = False
        correct_answer = self.game.correct_answer

        #If not judge and no guess submitted, submit guess
        if player != self.game.get_judge():
            if not self.game.did_guess(player):
                round_ended = self.game.process_guess(player, guess)
                self.add_return(output_list, f"{player} has made their guess.")
            else:
                self.add_return(output_list, f"{player} has already made their guess, and all guesses are final.")
        else:
            self.add_return(output_list, f"{self.game.get_judge()} can't guess! They know the answer!")

        #If all players have submitted, output points
        if round_ended == True:
            point_string = ""
            point_string += f"\n\nCorrect answer was: ***{correct_answer}***\nPoints:\n"
            for player in self.game.get_players():
                point_string += f"{player}: {self.game.get_points(player)}\n"

            self.add_return(output_list, point_string)
            
            #Check for winner or next prompt/judge
            winner = self.game.get_winner()
            if winner != None:
                self.add_return(output_list, f"Congrats, {winner}! You've won the game!")
            else:
                self.add_return(output_list, f"**{self.game.get_judge()}** is the judge. The category is:\n**{self.get_card_string(self.game.get_judge_card())}**\nPlease make a guess between {self.game.lowest_guess} and {self.game.highest_guess} based on the hint by using the **!guess** command.\nJudges use **/h** or **/hand** to see the correct answer and give your hint.")
    
        return output_list

    #Input: command string as defined in message.py for command helper functions
    #Output: the integer goal number passed by the player
    def change_goal_parse(self, parse_str):
        return int(parse_str[6:])

    #Input: player as defined in message.py for commands and integer goal_num from change_goal_parse
    #Output: add_return print for message handler
    async def change_goal(self, player, message):
        goal_num = self.change_goal_parse(message)
        if player in self.game.get_players():
            if goal_num != 0:
                self.game.win_points = goal_num

                return self.add_return([] if goal_num<1000 else self.add_return([], f"You've messed up, hun. Use **!end** to surrender if you even dare to **!start** in the first place."), f"{player} has changed the goal to {goal_num} points. Use **!start** to begin.")
            else:
                return self.add_return([], f"Don't input 0. I better not catch you doing it again. :eyes:")
        return self.add_return([], f"You can't edit a game you're not in, {player}. Use **!join** to join.")
    
    #Adds all expansions
    async def all(self, player, _message):
        output_str = ""
        output_str += await self.coders(player, None, raw=True) + "\n"
        output_str += await self.default(player, None, raw=True) + "\n"

        return self.add_return([], output_str)
    
    #Toggles CODERS expansion
    async def coders(self, _player, _message, raw=False):
        #Get old length and try to remove cards
        length = len(wd.spectrum_cards)
        wd.spectrum_cards = [card for card in wd.spectrum_cards if card not in wd.CODERS_CARDS]

        #If length changed, cards were removed. Else, add cards.
        if len(wd.spectrum_cards) < length:
            if not raw:
                return self.add_return([], "Removed CODERS expansion.")
            else:
                return "Removed CODERS expansion."
        else:
            wd.spectrum_cards += wd.CODERS_CARDS
            if not raw:
                return self.add_return([], "Added CODERS expansion.")
            else:
                return "Added CODERS expansion."
        
    #Toggles DEFAULT expansion
    async def default(self, _player, _message, raw=False):
        #Get old length and try to remove cards
        length = len(wd.spectrum_cards)
        wd.spectrum_cards = [card for card in wd.spectrum_cards if card not in wd.DEFAULT_CARDS and card not in wd.DEFAULT_POLITICAL_CARDS]

        #If length changed, cards were removed. Else, add cards.
        if len(wd.spectrum_cards) < length:
            if not raw:
                return self.add_return([], "Removed DEFAULT expansion.")
            else:
                return "Removed DEFAULT expansion."
        else:
            wd.spectrum_cards += wd.DEFAULT_CARDS
            wd.spectrum_cards += wd.DEFAULT_POLITICAL_CARDS
            if not raw:
                return self.add_return([], "Added DEFAULT expansion.")
            else:
                return "Added DEFAULT expansion."
            
    #Toggles BASE expansion
    async def base(self, _player, _message, raw=False):
        #Get old length and try to remove cards
        length = len(wd.spectrum_cards)
        wd.spectrum_cards = [card for card in wd.spectrum_cards if card not in wd.DEFAULT_CARDS]

        #If length changed, cards were removed. Else, add cards.
        if len(wd.spectrum_cards) < length:
            if not raw:
                return self.add_return([], "Removed BASE expansion.")
            else:
                return "Removed BASE expansion."
        else:
            wd.spectrum_cards += wd.DEFAULT_CARDS
            if not raw:
                return self.add_return([], "Added BASE expansion.")
            else:
                return "Added BASE expansion."