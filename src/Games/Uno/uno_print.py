from Games.Uno.uno import Uno
from Games.game_print import Game_Print
import Games.Uno.uno_pics as pics
from Games.Uno.uno_deck import Deck

class Uno_Print(Game_Print):
    def __init__(self):
        super().__init__()
        self.deck_look = pics()
        self.game = Uno()

        self.commands["^!(red|yellow|green|blue)$"] = [self.wild_color, self.input_parse]
        self.commands["^!(play|keep)"] = [self.drawn_card_handler, self.input_parse]
        self.commands["^!uno"] = [self.uno_handler, self.input_parse]
        self.commands["^!call"] = [self.call_handler, self.input_parse]
        self.commands["^!draw"] = [self.draw_handler, self.input_parse]

     # OVERRIDE #
    async def change_look(self, player, _look):
        if player in self.game.get_players():
            return self.add_return([], f"Feature not available for this game. Sorry! <3")
        else:
            return self.add_return([], f"You can't edit a game you aren't a part of, {player}. Use **!join** to join an unstarted game.")
    
    # OVERRIDE #
    #Returns the string to be displayed when the game is started
    def get_start_string(self) -> str:
        start_string = self.add_return([], f"Current top card is: ", self.deck_look.get_hand_pic([[self.game.top_card]], show_index=False))

        if "wild" in self.game.top_card:
            self.add_return(start_string, f"\nThe wild card's color is: **{self.game.top_card.color}**")

        self.add_return(start_string,f"\nCurrent Player order is {self.get_order_string()}")

        return self.add_return(f"\nIt is **{self.game.get_current_player()}**'s turn.\nUse **/h** or **/hand** to see your hand.")

    def get_order_string(self) -> str:
        order_string = []
        for i in len(self.game.get_players()) - 1:
            order_string.append(f"{self.game.get_players()[self.game.player_order[i]]}")
            if (i != len(self.game.get_players()) -1):
                order_string.append(" -> ")
        return order_string

    # OVERRIDE #
    #Returns the string to be displayed when the game is ended
    def get_end_string(self, _player) -> str:
        return f"The game has been ended early. There is no winner here."
    

        #Input: integer index parsed from string
    #Output: list of return statements using add_return
    async def select_card(self, player, card_index):
        if player in self.game.get_players() and self.game.game_started == True and not self.game.wild_in_play and not self.game.draw_card_in_play:
            #Check for valid index or return
            if(card_index >= len(self.game.hands[self.game.get_player_index(player)]) or card_index < 0):
                return []
              
            if player == self.game.get_current_player():
                card = self.game.hands[self.game.get_player_index(player)][card_index]
                if card.color == self.game.top_card.color or card.value == self.game.top_card.value:
                    self.game.top_card = card
                    self.game.card_select(player, card_index)
                    
    def input_parse(self, parse_str) -> list[str]:
        return [parse_str[1:]]
    
    def wild_color(self, player, color):
        output = 0
        if player == self.game.get_current_player():
            self.game.top_card.color = color
            self.game.current_player_index = self.game.get_next_player_index()
            
            if self.game.top_card.value == "wild4":
                skipped_player_index = self.game.current_player_index
                self.game.current_player_index = self.game.get_next_player_index
                for _ in range(4):
                    self.game.hands[skipped_player_index].append(Deck.draw_card())
                    self.add_return(output, f"{self.game.players[skipped_player_index]} drew 4 cards and lost their turn.")

            self.game.wild_in_play = False

            return f"Wild card had been changed to **{color}**!\n {self.get_start_string()}"

        return []

    def drawn_card_handler(self, player, choice):
        if player == self.game.get_current_player():
            if choice == "play":
                self.game.top_card = self.game.hands[self.game.get_player_index(player)].pop(-1)

            self.game.current_player_index = self.game.get_next_player_index()

            return f"{player} has chosen to {choice} their card.\n{self.get_start_string()}"

    def uno_handler(self, player):
        player_index = self.game.get_player_index(player)
        if self.game.game_started == True:
            #If you have only 1 card left or you have two and it's your turn to play a card you can declare uno
            if len(self.hands[player_index]) == 1 or (len(self.hands[player_index]) == 2 and player_index == self.game.current_player_index):
                self.game.uno_tracker[player_index] = True
                return f"{player} has declared Uno!"
            else:
                return f"{player} you cannot declare Uno you have to many cards!"

    def call_handler(self, player):
        output = []
        if self.game.game_started == True:
            #Call out everyone who hasn't declared uno who has 1 card
            for i in range(len(self.game.hands)):
                if len(self.game.hands[i]) == 1 and self.game.uno_tracker[i] == False and i != self.game.get_player_index(player):
                    for j in range(4):
                        self.game.hands[i].append(Deck.draw_card())
                    output = f"{output}\n {player} has called {self.game.players[i]} for not declaring Uno! {self.game.players[i]} draws 4 cards."
            
            if output == []:
                output = f"Good try {player}. There's nobody to call out this time."

            return output
    
    def draw_handler(self, player):
        if self.game.game_started == True and self.game.current_player_index == self.game.get_player_index(player) and not self.game.draw_card_in_play and not self.game.wild_in_play:
            self.game.draw_cards_til_matching()
            
                    
    