from random import randint

from Games.game_print import Game_Print
from Games.Juiced.juiced import Juiced

class Juiced_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        super().__init__()

        self.deck_look = None
        self.game = Juiced()
        
        #Add commands
        self.commands["^!insult$"] = [self.insult]
        self.commands["^!goal [0-9]+$"] = [self.change_goal, self.change_goal_parse]
    
    # OVERRIDE #
    async def change_look(self, player, _look):
        if player in self.game.get_players():
            return self.add_return([], f"Feature not available for this game. Sorry! <3")
        else:
            return self.add_return([], f"You can't edit a game you aren't a part of, {player}. Use **!join** to join an unstarted game.")
        
    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self, _player) -> str:
        return f"**{self.game.get_judge()}** is the judge. The card is:\n**{self.get_card_string(self.game.get_judge_card())}**"
    
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
            try:
                output_string += "!" + str(card_index) + ": " + self.get_card_string(hand[card_index]) + "\n"
            except:
                pass

        return output_string
    
    #Input: integer index parsed from string
    #Output: list of return statements using add_return
    async def select_card(self, player, card_index:int):
        output_list = []

        #If valid index for hands and mot judge, elif valid index for judge to select winner and judge plays valid card
        if (card_index >= 0) and (card_index < len(self.game.get_hand(player))) and (player != self.game.get_judge()):
            #If not judge
            if (self.game.judging == False):
                if self.game.card_select(player, card_index) == False:
                    return output_list
                self.add_return(output_list, f"Card submitted.")
                await self.update_hand(player)

                if self.game.judging == True:
                    self.add_return(output_list, f"All cards have been submitted. Please select the winner, {self.game.get_judge()}.\n{self.get_judge_string()}")
            else:
                self.add_return(output_list, f"Please wait your turn, {player}. **Judge {self.game.get_judge()}** is deciding the winner of this round.")

        elif (self.game.judging == True) and (player == self.game.get_judge()) and ((card_index >= 0) and (card_index < len(self.game.get_unholy_actions())) and (self.game.card_select(player, card_index) != False)):
            winner = self.game.get_winner()
            if winner == None:
                self.add_return(output_list, f"Congratulations, **{self.game.get_judge()}**.\n{self.get_point_string()}\n{self.get_start_string(player)}")
            else:
                self.add_return(output_list, f"Congratulations, **{winner}**. You've won the game!\n{self.get_point_string()}")
                self.game.end_game()

        return output_list

    #Gets the string that allows the judge to choose a card
    def get_judge_string(self):
        return f"**{self.get_card_string(self.game.get_judge_card())}**\n{self.get_hand_string_helper(self.game.get_unholy_actions())}"#[card for card in self.game.get_unholy_actions() if card != None])}"
    
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