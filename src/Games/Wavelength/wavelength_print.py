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
        #self.commands["^!all$"] = [self.all]
        self.commands["^!goal [0-9]+$"] = [self.change_goal]
        self.commands["^!guess -?[0-9]|(10)$"] = [self.make_guess]
    
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
        
    async def make_guess(self, player, message):
        output_list = []
        round_ended = False
        guess = int(message[7:])
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
            self.add_return(output_list, f"\n\nCorrect answer was: ***{correct_answer}***\nPoints:")
            for player in self.game.get_players():
                self.add_return(output_list, f"{player}: {self.game.get_points(player)}")
            
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
    
    # #Adds all expansions
    # async def all(self, player, _message):
    #     output_str = ""
    #     output_str += await self.coders(player, None, raw=True) + "\n"
    #     output_str += await self.cah(player, None, raw=True) + "\n"
    #     output_str += await self.apples(player, None, raw=True) + "\n"

    #     return self.add_return([], output_str)
    
    # #Toggles CODERS expansion
    # async def coders(self, _player, _message, raw=False):
    #     length = len(jd.WHITE_CARDS)
    #     jd.WHITE_CARDS = dict(set(jd.WHITE_CARDS.items()).symmetric_difference(set(jd.WHITE_CODERS.items())))
    #     jd.BLACK_CARDS = dict(set(jd.BLACK_CARDS.items()).symmetric_difference(set(jd.BLACK_CODERS.items())))
    #     if not raw:
    #         if length < len(jd.WHITE_CARDS):
    #             return self.add_return([], "Added CODERS expansion.")
    #         else:
    #             return self.add_return([], "Removed CODERS expansion.")
    #     else:
    #         if length < len(jd.WHITE_CARDS):
    #             return "Added CODERS expansion."
    #         else:
    #             return "Removed CODERS expansion."
        
    # #Toggles CAH expansion
    # async def cah(self, _player, _message, raw=False):
    #     length = len(jd.WHITE_CARDS)
    #     jd.WHITE_CARDS = dict(set(jd.WHITE_CARDS.items()).symmetric_difference(set(jd.WHITE_CAH.items())))
    #     jd.BLACK_CARDS = dict(set(jd.BLACK_CARDS.items()).symmetric_difference(set(jd.BLACK_CAH.items())))
    #     if not raw:
    #         if length < len(jd.WHITE_CARDS):
    #             return self.add_return([], "Added CAH expansion.")
    #         else:
    #             return self.add_return([], "Removed CAH expansion.")
    #     else:
    #         if length < len(jd.WHITE_CARDS):
    #             return "Added CAH expansion."
    #         else:
    #             return "Removed CAH expansion."
        
    # #Toggles APPLES expansion
    # async def apples(self, _player, _message, raw=False):
    #     length = len(jd.WHITE_CARDS)
    #     jd.WHITE_CARDS = dict(set(jd.WHITE_CARDS.items()).symmetric_difference(set(jd.WHITE_APPLES.items())))
    #     jd.BLACK_CARDS = dict(set(jd.BLACK_CARDS.items()).symmetric_difference(set(jd.BLACK_APPLES.items())))
    #     if not raw:
    #         if length < len(jd.WHITE_CARDS):
    #             return self.add_return([], "Added APPLES expansion.")
    #         else:
    #             return self.add_return([], "Removed APPLES expansion.")
    #     else:
    #         if length < len(jd.WHITE_CARDS):
    #             return "Added APPLES expansion."
    #         else:
    #             return "Removed APPLES expansion."