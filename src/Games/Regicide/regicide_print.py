from random import randint, shuffle

from Games.game_print import Game_Print
from Games.Regicide.regicide import Regicide

class Regicide_Print(Game_Print):
    HAND_PIC = True

    def __init__(self):
        super().__init__()

        self.game = Regicide()

        self.selecting_player = False
        
        #Add commands
        self.commands["^!insult$"] = [self.insult]
        self.commands["^!yield$"] = [self.yield_turn]
        self.commands["^!jester$"] = [self.jester]
        self.commands["^!execute$"] = [self.execute]
        self.commands["^!ex$"] = [self.execute]

    async def yield_turn(self, player):
        if self.game.yield_turn(player):
            return self.add_return([], f"You've yielded your turn, **{self.game.get_cur_player()}**. Defend yourself from {self.game.get_royal_atk()} damage!")
        else:
            return self.add_return([], f"You're unable to yield your turn, **{self.game.get_cur_player()}**.")
        
    async def jester(self, player):
        if self.game.jester(player):
            output_str = f"You've played the jester, **{self.game.get_cur_player()}**, causing the enemy to lose all immunities! Please select who will go next.\n"
            for person_index in range(len(self.game.get_players())):
                output_str += f"!{person_index} - {self.game.get_players()[person_index]}\n"
            self.selecting_player = True
            return self.add_return([], output_str)
        else:
            return self.add_return([], f"You're unable to play a jester, **{self.game.get_cur_player()}**.")
        
    async def execute(self, player):
        if player != self.game.get_cur_player():
            return self.add_return([], f"It's not your turn, {player}.")
        if self.game.defending:
            if sum([self.game.get_card_power(card) for card in self.game.get_cur_atk_def()]) < self.game.royal_atk:
                if self.game.execute(player) == True:
                    return self.add_return([], f"Uh oh! You lost! :(")
                else:
                    return self.add_return([], f"You need to defend yourself, {player}.")
            elif self.game.execute(player) == True:
                return self.add_return([], f"Enemy **{self.game.cur_royal.display()}** has **{self.game.get_royal_hp()} hp**! Kill them, **{self.game.get_cur_player()}**!\nYou have {self.game.jester_count} jesters remaining.\nUse **/h** or **/hand** to see your instruments of death.", self.deck_look.get_hand_pic([[self.game.get_cur_royal()]], show_index=False))
            else:
                return self.add_return([], f"You need to defend yourself, {player}.")
        else:
            cur_royal = self.game.cur_royal

            if len(self.game.get_cur_atk_def()) == 0:
                return self.add_return([], f'''You must attack or use "!yield" to pass your turn, {player}.''')

            self.game.execute(player)

            #If no regicide
            if cur_royal == self.game.cur_royal:
                return self.add_return([], f"Uh oh! Enemy **{self.game.cur_royal.display()}** is attacking for {self.game.royal_atk} damage! Defend yourself, {self.game.get_cur_player()}!", self.deck_look.get_hand_pic([[self.game.get_cur_royal()]], show_index=False))
            else:
                return self.add_return([], f"**Congrats on committing regicide!**\nEnemy **{self.game.cur_royal.display()}** has **{self.game.get_royal_hp()} hp**! Kill them, **{self.game.get_cur_player()}**!\nYou have {self.game.jester_count} jesters remaining.\nUse **/h** or **/hand** to see your instruments of death.", self.deck_look.get_hand_pic([[self.game.get_cur_royal()]], show_index=False))

    #Input: integer index parsed from string
    #Output: list of return statements using add_return
    async def select_card(self, player, card_index:int):
        #If selecting player instead of card
        if self.selecting_player:
            new_cur_player = self.game.get_players()[card_index]
            if self.game.change_cur_player(new_cur_player):
                self.selecting_player = False
                return self.add_return([], f"It is now **{new_cur_player}'s** turn!")
        else:
            #If card gets played
            played_card = self.game.get_hand(player)[card_index]
            if self.game.card_select(player, card_index):
                #Update hand if applicable.
                await self.update_hand(player)

                output = self.add_return([], f"**{player}** has played {played_card.display()}, for a total of {self.game.get_current_total()}", self.deck_look.get_hand_pic([[card for card in self.game.get_cur_atk_def()]], show_index=False))
                if self.game.defending:
                    output = self.add_return(output, f"Uh oh! Enemy **{self.game.cur_royal.display()}** is attacking for {self.game.royal_atk} damage! Defend yourself, {self.game.get_cur_player()}!", self.deck_look.get_hand_pic([[self.game.get_cur_royal()]], show_index=False))
                else:
                    output = self.add_return(output, f"Enemy **{self.game.cur_royal.display()}** has **{self.game.get_royal_hp()} hp**! Kill them, **{self.game.get_cur_player()}**!\nYou have {self.game.jester_count} jesters remaining.\nUse **/h** or **/hand** to see your instruments of death.", self.deck_look.get_hand_pic([[self.game.get_cur_royal()]], show_index=False))
                return output
        
        #If card doesn't get played, output nothing
        return []

    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self, _player) -> str:
        return f"Enemy **{self.game.cur_royal.display()}** has **{self.game.get_royal_hp()} hp**! Kill them, **{self.game.get_cur_player()}**!\nYou have {self.game.jester_count} jesters remaining.\nUse **/h** or **/hand** to see your instruments of death."
    
    #Get string of hand to print for player at given index
    def get_hand_string(self, player):
        player_index = self.game.get_players().index(player)
        output_string = f"Hand:\n"
        for card in [card.display() for card in sorted(self.game.hands[player_index], key=lambda x: x.to_int_runs())]:
            output_string += f"{card}, "
        output_string = output_string[:-2] + "\n"
        for card in [card for card in sorted(self.game.hands[player_index], key=lambda x: x.to_int_runs())]:
            output_string += f"!{self.game.hands[player_index].index(card)},\t\t"
        output_string = output_string[:-3] + "\n"

        return output_string

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