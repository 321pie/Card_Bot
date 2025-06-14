from random import randint, shuffle

from Games.game_print import Game_Print
from Games.Juiced.juiced import Juiced
import Games.Juiced.juiced_deck as jd

class Juiced_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        super().__init__()

        self.deck_look = None
        self.game = Juiced()
        self.scrambled_unholy_actions:list[list] = []
        
        #Add commands
        self.commands["^!wager [0-9]+$"] = [self., self.]
        self.commands["^!is [a-z0-9]+$"] = [self., self.]
        self.commands["^!do [a-z0-9]+$"] = [self., self.]
        self.commands["^!pass$"] = [self.]
        self.commands["^!all$"] = [self.all]
        self.commands["^!coders$"] = [self.coders]
    
    # OVERRIDE #
    async def change_look(self, player, _look):
        if player in self.game.get_players():
            return self.add_return([], f"Feature not available for this game. Sorry! <3")
        else:
            return self.add_return([], f"You can't edit a game you aren't a part of, {player}. Use **!join** to join an unstarted game.")
        
    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self, _player) -> str:
        return f"**{self.game.get_judge()}** is the judge. The card is:\n**{self.get_card_string(self.game.get_judge_card())}**\nPlease play **{self.game.get_judge_card().suit}** card(s).\nUse **/h** or **/hand** to see your hand."
    
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
    #Output: the integer goal number passed by the player
    def change_goal_parse(self, parse_str):
        return [int(parse_str[6:])]

    #Input: player as defined in message.py for commands and integer goal_num from change_goal_parse
    #Output: add_return print for message handler
    async def change_goal(self, player, goal_num):
        if player in self.game.get_players():
            if goal_num != 0:
                self.game.win_points = goal_num

                return self.add_return([] if goal_num<1000 else self.add_return([], f"You've messed up, hun. Use **!end** to surrender if you even dare to **!start** in the first place."), f"{player} has changed the goal to {goal_num} points. Use **!start** to begin.")
            else:
                return self.add_return([], f"Don't input 0. I better not catch you doing it again. :eyes:")
        return self.add_return([], f"You can't edit a game you're not in, {player}. Use **!join** to join.")
    

    
    #Adds all expansions
    async def all(self, player):
        output_str = ""
        output_str += await self.coders(player, raw=True) + "\n"
        output_str += await self.cah(player, raw=True) + "\n"
        output_str += await self.apples(player, raw=True) + "\n"

        return self.add_return([], output_str)
    
    #Toggles CODERS expansion
    async def coders(self, _player, raw=False):
        length = len(jd.WHITE_CARDS)
        jd.WHITE_CARDS = dict(set(jd.WHITE_CARDS.items()).symmetric_difference(set(jd.WHITE_CODERS.items())))
        jd.BLACK_CARDS = dict(set(jd.BLACK_CARDS.items()).symmetric_difference(set(jd.BLACK_CODERS.items())))
        if not raw:
            if length < len(jd.WHITE_CARDS):
                return self.add_return([], "Added CODERS expansion.")
            else:
                return self.add_return([], "Removed CODERS expansion.")
        else:
            if length < len(jd.WHITE_CARDS):
                return "Added CODERS expansion."
            else:
                return "Removed CODERS expansion."