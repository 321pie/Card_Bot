from random import randint, shuffle

from Games.game_print import Game_Print
from Games.Jeopardy.jeopardy import Jeopardy
import Games.Jeopardy.questions as qs

class Jeopardy_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        super().__init__()

        self.deck_look = None
        self.game = Jeopardy
        
        #Add commands
        self.commands = {
            "^!join$": [self.join],
            "^!jion$": [self.join],
            "^!unjoin$": [self.unjoin],
            "^!unjion$": [self.unjoin],
            "^!start$": [self.start],
            "^!end$": [self.end_game],
        }
        self.commands["^!wager [0-9]+$"] = [self.wager, self.wager_parse]
        self.commands["^!is [a-z0-9]+$"] = [self.guess, self.guess_parse]
        self.commands["^!do [0-9] [0-9]+$"] = [self.select_question, self.select_question_parse]
        self.commands["^!pass$"] = [self.pass_turn]
        self.commands["^!all$"] = [self.all]
        self.commands["^!coders$"] = [self.coders]
        self.commands["^!std$"] = [self.standard]
    
    # OVERRIDE #
    async def change_look(self, player, _look):
        if player in self.game.get_players():
            return self.add_return([], f"Feature not available for this game. Sorry! <3")
        else:
            return self.add_return([], f"You can't edit a game you aren't a part of, {player}. Use **!join** to join an unstarted game.")
        
    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self, _player) -> str:
        return f"**{self.game.get_play_player()}** is selecting the first question.\n\n" + self.get_board()
    
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
    
    #Input: command string as defined in message.py for command helper functions
    #Output: the integer wager passed by the player
    def wager_parse(self, parse_str):
        return [int(parse_str[7:])]

    #Input: player as defined in message.py for commands and integer wager from wager_parse
    #Output: add_return print for message handler
    async def wager(self, player, wager):
        cur_player = self.game.get_play_player()
        max_wager_amount = self.game.get_increase_amount() * self.game.get_row_count() * 2

        #If correct player, wager not set, and valid wager value, set wager
        if player != cur_player:
            return self.add_return([], f"Only **{cur_player}** can wager and play this round.")
        if self.game.get_wager() != None:
            return self.add_return([], f"The wager has already been set. Please answer the question.")
        if 0 < wager < max_wager_amount:
            return self.add_return([], f"You must wager a positive amount between 0 and {max_wager_amount}.")
        else:
            if self.game.wager(wager) == True:
                return self.add_return([], f"The wager has been set. Please answer the following question with the !is command:\n{self.game.get_question()}")
            else:
                return self.add_return([], "Uh, oh! Something went wrong with your wager! Blame Andrew! :skull:")
            
    #Input: command string as defined in message.py for command helper functions
    #Output: the guess passed by the player
    def guess_parse(self, parse_str):
        return parse_str[1:]
    
    #Input: player as defined in message.py for commands and str guess from guess_parse
    #Output: add_return print for message handler
    async def guess(self, player, guess):
        #Check to make sure that guessing is valid
        if self.game.get_answer == None:
            return self.add_return([], f"Question must be selected using !do command before guessing can begin.")

        #Check for daily double shenanigans
        if self.game.is_daily_double():
            if player != self.game.get_play_player():
                return self.add_return([], f"Only **{self.game.get_play_player()}** can guess.")
            elif guess == self.game.get_answer():
                return self.add_return([], f"Congrats, **{player}**! You've gained {self.game.guess(player, guess)} points.")
            else:
                return self.add_return([], f"Uh oh, **{player}**! You've lost {self.game.guess(player, guess) * -1} points. Please select the next question.\n\n{self.get_board()}")
            
        #If not daily double, 
        else:
            if guess == self.game.get_answer():
                return self.add_return([], f"Congrats, **{player}**! You've gained {self.game.guess(player, guess)} points.")
            else:
                return self.add_return([], f"Uh oh, **{player}**! You've lost {self.game.guess(player, guess) * -1} points. You can try again or pass the round with the !pass command.")
        
    #Input: command string as defined in message.py for command helper functions
    #Output: the question passed by the player
    def select_question_parse(self, parse_str):
        return parse_str[1:]
    
    #Input: player as defined in message.py for commands and str from select_question_parse in form row col
    #Output: add_return print for message handler
    async def select_question(self, player, question_index:str):
        #Turn question into row and column
        row, column = question_index.split(" ")
        column = column / self.game.get_increase_amount()

        #Check for correct player
        if player != self.game.get_play_player():
            return self.add_return([], f"Only **{self.game.get_play_player()}** can select the question.")

        #Print out response
        question = self.game.select_question(player, row, column)
        if question == None:
            return self.add_return([], f"That question is invalid. Please select an unanswered question.")
        elif self.game.is_daily_double():
            return self.add_return([], f"Congrats, **{self.game.get_play_player()}**! That's the daily double! Enter a wager with the !wager command!")
        else:
            return self.add_return([], f"Please answer the following question with the !is command:\n{question}")
        
    #Input: player as defined in message.py for commands and integer goal_num from change_goal_parse
    #Output: add_return print for message handler
    async def pass_turn(self, player):
        if player in self.game.get_players():
            if self.game.pass_round(player):
                return self.add_return([], f"All players have passed the round. **{self.game.get_play_player()}**, please select the next question.\n\n{self.get_board()}")
            else:
                return self.add_return([], f"**{player}** has passed this round.")
        else:
            return self.add_return([], f"**{player}** is not in this game.")
    
    #Returns a string to output to the player that shows the board
#TODO: do it
    def get_board(self) -> str:
        return "Not Yet Implemented :("
    
    #Adds all expansions
    async def all(self, player):
        output_str = ""
        output_str += await self.coders(player, raw=True) + "\n"
        output_str += await self.default(player, raw=True) + "\n"

        return self.add_return([], output_str)
    
    #Toggles CODERS expansion
    async def standard(self, _player, raw=False):
        length = len(self.game.questions)
        self.game.questions = dict(set(self.game.questions.items()).symmetric_difference(set(qs.STD_QUOTES.items())))
        if not raw:
            if length < len(self.game.questions):
                return self.add_return([], "Added STD expansion.")
            else:
                return self.add_return([], "Removed STD expansion.")
        else:
            if length < len(self.game.questions):
                return "Added STD expansion."
            else:
                return "Removed STD expansion."
    
    #Toggles CODERS expansion
    async def coders(self, _player, raw=False):
        length = len(self.game.questions)
        self.game.questions = dict(set(self.game.questions.items()).symmetric_difference(set(qs.CODERS_QUOTES.items())))
        if not raw:
            if length < len(self.game.questions):
                return self.add_return([], "Added CODERS expansion.")
            else:
                return self.add_return([], "Removed CODERS expansion.")
        else:
            if length < len(self.game.questions):
                return "Added CODERS expansion."
            else:
                return "Removed CODERS expansion."