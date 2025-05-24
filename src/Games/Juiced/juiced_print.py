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
        self.commands["^!insult$"] = [self.insult]
        self.commands["^!shuffle$"] = [self.shuffle]
        self.commands["^!all$"] = [self.all]
        self.commands["^!apples$"] = [self.apples]
        self.commands["^!cah$"] = [self.cah]
        self.commands["^!coders$"] = [self.coders]
        self.commands["^!goal [0-9]+$"] = [self.change_goal, self.change_goal_parse]
        self.commands["^!hand [0-9]+$"] = [self.change_hand_length, self.change_hand_length_parse]
    
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

    #Returns the string from a hand
    def get_card_string(self, card):
        return card.value
    
    #Gets a hand
    def get_hand_string(self, player):
        if player in self.game.get_players():
            return self.get_hand_string_helper(self.game.get_hand(player))
        else:
            return f"You aren't in the game {player}, so you don't have a hand."
        
    #Returns the string for someone's hand
    def get_hand_string_helper(self, hand):
        output_string = ""
        for card_index in range(len(hand)):
            output_string += "!" + str(card_index) + ": " + self.get_card_string(hand[card_index]) + "\n"

        return output_string
    
    #Returns the string for judge's hand
    def get_judge_hand_string(self, hand):
        output_string = ""
        for card_index in range(len(hand)):
            output_string += "!" + str(card_index) + ": " + self.get_judge_hand_string_helper([self.get_card_string(hand[card_index][multiple_card_index]) for multiple_card_index in range(len(hand[card_index]))]) + "\n"

        return output_string
    
    #Returns the string for a list of cards for the judge hand
    def get_judge_hand_string_helper(self, cards):
        output_string = ""
        for card in cards:
            output_string += card + ", "

        return output_string[:-2]
    
    #Input: integer index parsed from string
    #Output: list of return statements using add_return
    async def select_card(self, player, card_index:int):
        output_list = []

        #If valid index for hands and not judge, elif valid index for judge to select winner
        if (card_index >= 0) and (card_index < len(self.game.get_hand(player))) and (player != self.game.get_judge()):
            #If not judge
            if (self.game.judging == False):
                if self.game.card_select(player, card_index) == False:
                    return output_list
                
                self.add_return(output_list, f"Card submitted.")
                await self.update_hand(player)

                if self.game.judging == True:
                    self.scrambled_unholy_actions = [action_list for action_list in self.game.get_unholy_actions() if len(action_list) != 0]
                    shuffle(self.scrambled_unholy_actions)
                    self.add_return(output_list, f"All cards have been submitted. Please select the winner, **{self.game.get_judge()}**.\n{self.get_judge_string()}")
            else:
                self.add_return(output_list, f"Please wait your turn, {player}. Judge **{self.game.get_judge()}** is deciding the winner of this round.")

        elif (self.game.judging == True) and (player == self.game.get_judge()) and (card_index >= 0) and (card_index < len(self.scrambled_unholy_actions)):
            #Decode index since we scrambled the array
            unholy_card_index = card_index
            card_index = self.game.get_unholy_actions().index(self.scrambled_unholy_actions[card_index])

            self.game.card_select(player, card_index)
            winner = self.game.get_winner()
            if winner == None:
                self.add_return(output_list, f"Chosen card(s): **{self.get_judge_hand_string_helper([self.get_card_string(card) for card in self.scrambled_unholy_actions[unholy_card_index]])}**\nCongratulations, **{self.game.get_judge()}**!\n{self.get_point_string()}\n{self.get_start_string(player)}")
                self.scrambled_unholy_actions = []
            else:
                self.add_return(output_list, f"Congratulations, **{winner}**! You've won the game!\n{self.get_point_string()}")
                self.game.end_game()

        return output_list

    #Gets the string that allows the judge to choose a card
    def get_judge_string(self):
        return f"**{self.get_card_string(self.game.get_judge_card())}**\n{self.get_judge_hand_string(self.scrambled_unholy_actions)}"
    
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
    
    #Input: command string as defined in message.py for command helper functions
    #Output: the integer goal number passed by the player
    def change_hand_length_parse(self, parse_str):
        return [int(parse_str[6:])]

    #Input: player as defined in message.py for commands and integer goal_num from change_goal_parse
    #Output: add_return print for message handler
    async def change_hand_length(self, player, hand_len):
        if player in self.game.get_players():
            if (hand_len >= 5) and (hand_len <= 20):
                self.game.hand_len = hand_len
            else:
                return self.add_return([], f"Invalid hand size. Please input a number between 5 and 20.")
        return self.add_return([], f"You can't edit a game you're not in, {player}. Use **!join** to join.")

    #Toggles the game to get new hands for every player every round
    async def shuffle(self, _player):
        self.game.shuffle = not self.game.shuffle
        return self.add_return([], "Hands will be reset every round." if self.game.shuffle==True else "Hands will not be reset every round.")
    
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
        
    #Toggles CAH expansion
    async def cah(self, _player, raw=False):
        length = len(jd.WHITE_CARDS)
        jd.WHITE_CARDS = dict(set(jd.WHITE_CARDS.items()).symmetric_difference(set(jd.WHITE_CAH.items())))
        jd.BLACK_CARDS = dict(set(jd.BLACK_CARDS.items()).symmetric_difference(set(jd.BLACK_CAH.items())))
        if not raw:
            if length < len(jd.WHITE_CARDS):
                return self.add_return([], "Added CAH expansion.")
            else:
                return self.add_return([], "Removed CAH expansion.")
        else:
            if length < len(jd.WHITE_CARDS):
                return "Added CAH expansion."
            else:
                return "Removed CAH expansion."
        
    #Toggles APPLES expansion
    async def apples(self, _player, raw=False):
        length = len(jd.WHITE_CARDS)
        jd.WHITE_CARDS = dict(set(jd.WHITE_CARDS.items()).symmetric_difference(set(jd.WHITE_APPLES.items())))
        jd.BLACK_CARDS = dict(set(jd.BLACK_CARDS.items()).symmetric_difference(set(jd.BLACK_APPLES.items())))
        if not raw:
            if length < len(jd.WHITE_CARDS):
                return self.add_return([], "Added APPLES expansion.")
            else:
                return self.add_return([], "Removed APPLES expansion.")
        else:
            if length < len(jd.WHITE_CARDS):
                return "Added APPLES expansion."
            else:
                return "Removed APPLES expansion."
    
    #Procures an insult from a hand-crafted list of premium rudeness
    async def insult(self, _player):
        return self.add_return([], self.INSULT_LIST[randint(0, len(self.INSULT_LIST)-1)])
    
    INSULT_LIST = [
        "You could do better.",
        "If you were a spice, you'd be flour.",
        "I smell something burning. Were you trying to think again?",
        "May the chocolate chips in your cookies always turn out to be raisins.",
        "Where's your off button?",
        "It’s great to see that you don’t let your education get in the way of your ignorance.",
        "You’re the reason tubes of toothpaste have instructions on them.",
        "Stupidity isn't a crime. You’re free to go.",
        "I would describe your personality as a vibrant shade of beige.",
        "I have 90 billion nerves, and you’re on every single one of them.",
        "I don’t understand, but I also don’t care, so it works out nicely.",
        "I might not be perfect, but at least I'm not you.",
        "Where have you been all my life? You should go back there.",
        "I'd slap you, but then it would be animal abuse.",
        "Roses are red, violets are blue, I have 5 fingers and the 3rd one’s for you.",
        "It’s kind of sad watching you fit your entire vocabulary into one sentence.",
        "Honestly, I'm just impressed you could read this.",
        "I have neither the time nor the crayons necessary to explain this to you.",
        "You do you. Because God knows no one else will.",
        "What doesn't kill you disappoints the rest of us.",
        "You'll go far someday. And I hope you stay there.",
        "If I gave you a penny for your thoughts, I'd get change back.",
        "Our parents told us we could be anything, and I can see you wanted to be a disappointment.",
        "Your birth control of choice appears to be your personality.",
        "I'd love to help you out. You can leave by right-clicking the server.",
        "Don't be ashamed of who you are. That's your parents' job.",
        "That sounds like a you problem.",
        "I would insult you, but every mean thing I could say would just be a description.",
        "I've lived a very happy life. Until I met you, that is.",
        "How is it that you know everything except when to shut up?",
        "I'm sure you'd make a great martial arts instructor. You have a very punchable face.",
        "Talk to you? I'd really rather die, thanks.",
        'Whoever came up with the term "Ignorance is bliss" probably did so after meeting you.',
        "If you actually listened when you talked, you'd want to leave the conversation too.",
        "Only a robot could have the patience to talk to you.\n*Hello there.*"
    ]