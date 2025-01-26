from Games.Uno.uno import Uno
from Games.game_print import Game_Print
from Games.Uno.uno_pics import UnoPics
from Games.Uno.uno_deck import Deck

class Uno_Print(Game_Print):
    HAND_PIC = True

    def __init__(self):
        super().__init__()
        self.deck_look = UnoPics()
        self.game = Uno()

        self.commands["^!(red|yellow|green|blue)$"] = [self.wild_color, self.input_parse]
        self.commands["^!(play|keep)$"] = [self.drawn_card_handler, self.input_parse]
        self.commands["^!(declare|d)$"] = [self.uno_handler]
        self.commands["^!call"] = [self.call_handler]
        self.commands["^!draw"] = [self.draw_handler]
        self.commands["^!house"] = [self.house_handler]
        self.commands["^!stack"] = [self.stack_handler]
        self.commands["^!(challenge|accept)$"] = [self.four_wild_handler, self.input_parse]
        self.commands["^!fourchal"] = [self.four_challenge_handler]
        self.commands["^!rotate"] = [self.rotate_handler]
        self.commands["^!swap$"] = [self.swap_handler]
        self.commands["^!swap [0-9]$"] = [self.swap_player_handler, self.input_parse]
        self.commands["^!jump"] = [self.jump_handler]


     # OVERRIDE #
    async def change_look(self, player, _look):
        if player in self.game.get_players():
            return self.add_return([], f'''Feature not available for this game. Sorry! <3''')
        else:
            return self.add_return([], f'''You can't edit a game you aren't a part of, {player}. Use **!join** to join an unstarted game.''')
    
    # OVERRIDE #
    async def start(self, player):
        if player in self.game.get_players():
            if self.game.start_game():
                #Initialize local vars
                for _ in self.game.get_players():
                    self.end.append(False)
                    self.hand_messages.append(None)
                    
                return self.game.get_round_string(f"Game started by {player}.")
            else:
                return self.add_return([], "Something went wrong when starting the game.")
        else:
            return self.add_return([], f"You can't start a game you aren't queued for, **{player}**. Use **!join** to join the game.")

    # OVERRIDE #
    #Returns the string to be displayed when the game is ended
    def get_end_string(self, _player) -> str:
        return f"The game has been ended early. There is no winner here."
    

        #Input: integer index parsed from string
    #Output: list of return statements using add_return
    async def select_card(self, player, card_index) -> list:
        if player in self.game.get_players() and self.game.game_started == True and not self.game.wild_in_play and not self.game.draw_card_in_play:
            #Check for valid index or return
            if(card_index >= len(self.game.hands[self.game.get_player_index(player)]) or card_index < 0):
                return []
              
            if player == self.game.get_current_player():
                card = self.game.hands[self.game.get_player_index(player)][card_index]
                if card.color == self.game.top_card.color or card.value == self.game.top_card.value or card.value.find("wild") != -1:
                    self.game.top_card = card
                    output = self.game.card_select(player, card_index)
                    await self.update_hand(player)
                    return output
                    
    def input_parse(self, parse_str) -> list[str]:
        return [parse_str[1:]]
    
    async def wild_color(self, player, color):
        output = ""
        if player == self.game.get_current_player():
            self.game.top_card.color = color
            output += f"Wild card has been made into {color}."
            self.game.current_player_index = self.game.get_next_player_index()
            
            if self.game.top_card.value == "wild4":
                skipped_player_index = self.game.current_player_index
                self.game.current_player_index = self.game.get_next_player_index()
                for _ in range(4):
                    self.game.hands[skipped_player_index].append(self.game.deck.draw_card())
                output += f"\n**{self.game.players[skipped_player_index]} drew 4 cards and lost their turn.**"
            
            self.game.wild_in_play = False
            return self.game.get_round_string(output)

        return []

    async def drawn_card_handler(self, player, choice):
        if self.game.get_player_index(player) == self.game.current_player_index and self.game.draw_card_in_play == True:
            output = f'''{player} has chosen to {choice} their card.\n'''
            if choice == "play":
                self.game.top_card = self.game.hands[self.game.get_player_index(player)].pop(-1)
                output += self.game.action_card_handler(self.game.get_player_index(player))
                await self.update_hand(player)
            self.game.draw_card_in_play = False
            return self.game.get_round_string(output)

    async def uno_handler(self, player):
        player_index = self.game.get_player_index(player)
        if self.game.game_started == True:
            #If you have only 1 card left or you have two and it's your turn to play a card you can declare uno
            if (len(self.game.hands[player_index]) == 1 or (len(self.game.hands[player_index]) == 2) and player_index == self.game.current_player_index):
                self.game.uno_tracker[player_index] = True
                return self.add_return([], f'''{player} has declared Uno!''')
            else:
                return self.add_return([], f'''{player} you cannot declare Uno you have to many cards!''')

    async def call_handler(self, player):
        output = []
        if self.game.game_started == True:
            #Call out everyone who hasn't declared uno who has 1 card
            for i in range(len(self.game.hands)):
                if len(self.game.hands[i]) == 1 and self.game.uno_tracker[i] == False and i != self.game.get_player_index(player):
                    print(f"Called out {self.game.players[i]}")
                    for j in range(4):
                        self.game.hands[i].append(Deck().draw_card())
                    output = f'''{output}\n {player} has called out {self.game.players[i]} for not declaring Uno! {self.game.players[i]} draws 4 cards.'''
            
            if output == []:
                output = f'''Good try {player}. There's nobody to call out this time.'''

            return self.add_return([], output)
    
    async def draw_handler(self, player):
        if self.game.game_started == True and self.game.current_player_index == self.game.get_player_index(player) and not self.game.draw_card_in_play and not self.game.wild_in_play:
            if self.game.stackAmount > 0:
                for _ in range(self.game.stackAmount):
                    self.game.hands[self.game.current_player_index].append(Deck().draw_card())
                output = f"{self.game.get_current_player()} drew {self.game.stackAmount}!"
                self.game.stackAmount = 0
                self.game.current_player_index = self.game.get_next_player_index()
                return self.game.get_round_string(output)
            else:
                return self.add_return([], self.game.draw_cards_til_matching())
    
    #Toggle on and off all house rules
    async def house_handler(self, player):
        if player in self.game.get_players():
            self.game.house_rules = not self.game.house_rules
            return self.add_return([], f"{player} has changed the game to{'' if self.game.house_rules else 'not'} have all the house rules! Use !house to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Toggle on and off stacking rule
    async def stack_handler(self, player):
        if player in self.game.get_players():
            self.game.stack = not self.game.stack
            return self.add_return([], f"{player} has changed the game to{'' if self.game.stack else 'not'} have stacking allowed for any + card! Use !stack to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Toggle on and off challenge rule
    async def four_challenge_handler(self, player):
        if player in self.game.get_players():
            self.game.challenge = not self.game.challenge
            return self.add_return([], f"{player} has changed the game to{'' if self.game.challenge else 'not'} have challenging allowed when a +4 is played! Use !fourchal to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Toggle on and off rotation rule
    async def rotate_handler(self, player):
        if player in self.game.get_players():
            self.game.rotate = not self.game.rotate
            return self.add_return([], f"{player} has changed the game to{'' if self.game.rotate else 'not'} have rotation of hands when a 0 is played! Use !rotate to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Toggle on and off swap rule
    async def swap_handler(self, player):
        if player in self.game.get_players():
            self.game.swap = not self.game.swap
            return self.add_return([], f"{player} has changed the game to{'' if self.game.swap else 'not'} have swapping of hands when a 7 is played! Use !swap to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        

    #Toggle on and off jump rule
    async def jump_handler(self, player):
        if player in self.game.get_players():
            self.game.jump = not self.game.jump
            return self.add_return([], f"{player} has changed the game to{'' if self.game.jump else 'not'} have jumping in allowed! Use !jump to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        

    #handles the player choosing who to swap with
    async def swap_player_handler(self, player, choice):
        return []

    #handles the player deciding to challenge or not
    async def four_wild_handler(self, player, choice):
        return []