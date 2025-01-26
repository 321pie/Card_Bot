from math import factorial, floor
import random

from Games.Uno.uno_deck import Card
from Games.Uno.uno_deck import Deck
import Games.game as game
from Games.Uno.uno_pics import UnoPics

class Uno(game.Game):
    def __init__(self):
        super().__init__()
        self.deck = Deck()
        self.hands:list[list[Card]] = [] #The hands of each player, indexed the same as the players
        self.top_card: Card #Card to start with and what everyone will play off of
        self.player_order: list[int] = [] # Player order list with player indexes as values
        self.current_player_index: int = 0 # Index of player whose turn it is to play
        self.wild_in_play: bool = False #Blocks players from playing until wild color is chosen
        self.draw_card_in_play: bool = False # Blocks players from playing until player has chosen to keep/play drawn card
        self.uno_tracker: list[bool] = [] # list to keep track of who has called uno or not. Indexed the same as players
        self.house_rules: bool = False # Flag that indicates if playing with all house rules available
        self.stack: bool = False #Flag that indicates if playing with stacking
        self.challenge:bool = False #Flag that indicates if playing with challenges
        self.rotate:bool = False #Flag that indicates if playing with rotations when a 0 is played
        self.swap: bool = False #Flag that indicates if playing with swaps when a 7 is played 
        self.jump: bool = False #Flag that indicates that jumping is is allowed if player has same card
        self.stackAmount: int = 0 #Amount the stack has that the next player will need to draw
        self.stack_in_play: bool = False #Flag that says that a stack is going and players can only play a +2 or +4

    #Initializes the game on start
    #Returns 0 on success, -1 on failure
    def initialize_game(self) -> bool:
        for i in range(len(self.players)):
            self.player_order.append(self.get_player_index(self.players[i]))
            self.uno_tracker.append(False)
        random.shuffle(self.player_order)
        self.current_player_index = self.player_order[0]
        self.top_card = self.deck.get_start()
        
        #Get initial Player hands
        self.hands = self.deck.get_hands(len(self.players))
        return True
    
    def add_return(self, return_list, return_string, file=None, index=None):
        if(index == None):
            index = len(return_list)

        if(index >= len(return_list)):
            return_list.append([return_string, file])
        elif(index < len(return_list)):
            return_list.insert(index, [return_string, file])

        return return_list
        
    # OVERRIDE #
    #Returns and removes card at given index
    #Returns card on success, False on failure
    def card_select(self, player, card_index:int) -> list:
        if player in self.players:
            player_index = self.players.index(player)
            if (card_index < len(self.hands[player_index])) and (card_index >= 0):
                self.hands[player_index].pop(card_index)
                return self.get_round_string(self.process_card_select(player_index))
        return []
    
    def process_card_select(self, player_index:int) -> str:
        output = ""
        #Check if player played their last card
        if len(self.hands[player_index]) == 0:
            output = f"{self.players[player_index]} has played their last card and won the game!"
            self.end_game()
            return output

        return self.action_card_handler(player_index)

    def get_current_player(self):
        return self.players[self.current_player_index]
    
    def get_next_player_index(self):
        if self.current_player_index == self.player_order[-1]:
            return self.player_order[0]
        else:
            return self.player_order[self.player_order.index(self.current_player_index) + 1]
        
    #This function will draw cards from the deck until you pull a wild or a card that matches color/value
    def draw_cards_til_matching(self) -> str:
        card = self.deck.draw_card()
        self.hands[self.current_player_index].append(card)
        count = 1
        while(card.color != self.top_card.color and card.value != self.top_card.value and card.value.find("wild") == -1):
            card = self.deck.draw_card()
            self.hands[self.current_player_index].append(card)
            count += 1
        self.draw_card_in_play = True
        return f"**{self.players[self.current_player_index]} drew {count} cards.**\n {self.players[self.current_player_index]} can now choose whether to !play or !keep the usable card."
    
    def check_player_has_usable_card(self) -> bool:
        hand = self.hands[self.current_player_index]
        found = False

        for i in range(len(hand)):
            if hand[i].color == self.top_card.color or hand[i].value == self.top_card.value or hand[i].value.find("wild") != -1:
                found = True
                break
        return found
    
    def check_player_has_plus_two(self) -> bool:
        hand = self.hands[self.current_player_index]
        found = False

        for i in range(len(hand)):
            if hand[i].value.find("draw2") != -1:
                found = True
                break
        return found
    
    def check_player_has_plus_four(self) -> bool:
        hand = self.hands[self.current_player_index]
        found = False

        for i in range(len(hand)):
            if hand[i].value.find("wild4") != -1:
                found = True
                break
        return found

    #Ends the game by resetting every variable
    def end_game(self):
        self.players = []
        self.hands = []
        self.top_card = None 
        self.player_order = []
        self.current_player_index = 0
        self.wild_in_play = False 
        self.draw_card_in_play= False
        self.uno_tracker = []
        self.game_started = False 

    def get_round_string(self, input) -> list:
        turn_string = self.add_return([], input)
        if self.game_started == True and self.wild_in_play == False:
            self.add_return(turn_string, f"Current top card is: ", UnoPics().get_hand_pic([[self.top_card]], show_index=False))
            if self.top_card.value.find("wild") != -1:
                self.add_return(turn_string, f"\nThe wild card's color is: **{self.top_card.color}**")

            #Check initially if someone had to draw cards and now waiting for decision
            if self.check_player_has_usable_card() == False:
                #If someone has declared uno draws cards, their uno declaration gets reset
                if len(self.hands[self.current_player_index]) == 1:
                    self.uno_tracker[self.current_player_index] = False
                return self.add_return(turn_string, self.draw_cards_til_matching())

            self.add_return(turn_string, f"Current Player order is {self.get_order_string()}")

            numCards = ""
            for i in range(len(self.players)):
                numCards += f"\n{self.players[i]}: {len(self.hands[self.get_player_index(self.players[i])])} Cards"
            return self.add_return(turn_string, f"{numCards} \n It is **{self.get_current_player()}**'s turn.")
        return turn_string
    
    def get_order_string(self) -> str:
        output =""
        for i in range(len(self.get_players())):
            if self.player_order[i] == self.current_player_index:
                output += f"**{self.get_players()[self.player_order[i]]}**"
            else:
                output += f"{self.get_players()[self.player_order[i]]}"
            if i != (len(self.get_players()) - 1):
                output +=" -> "
        return output
    
    def action_card_handler(self, player_index: int):
        if self.top_card.value.find("wild") != -1:
            self.wild_in_play = True
            self.draw_card_in_play = False
            return f"Wild card has been played! {self.get_current_player()} gets to choose what color it becomes."  
        elif self.top_card.value == "skip":
            return self.skip_played(player_index)
        elif self.top_card.value == "reverse":
            return self.reverse_played()
        elif self.top_card.value == "draw2":
            return self.draw_two_played()
        else:
            output = f"{self.get_current_player()} has played!"
            self.current_player_index = self.get_next_player_index()     
            return output

    def draw_two_played(self) -> str:
        past_player = self.get_current_player()
        self.current_player_index = self.get_next_player_index()
        self.stackAmount += 2
        if self.stack and self.check_player_has_plus_two():
            self.stack_in_play = True
            return f"**{past_player}** has played a +2! \n Current Stack is now **+{self.stackAmount}**!\n**{self.get_current_player()}** can now choose to continue the stack or take the cards with **!draw**"
        else:
            self.stack_in_play = False
            skipped_player = self.current_player_index
            self.current_player_index = self.get_next_player_index()     
            for _ in range(self.stackAmount):
                self.hands[skipped_player].append(self.deck.draw_card())
            output = f"**{self.players[skipped_player]}** drew **{self.stackAmount}** cards and lost their turn!"
            self.stackAmount = 0
            return output
    
    def wild_four_played(self) -> str:
        past_player = self.get_current_player()
        self.current_player_index = self.get_next_player_index()
        self.stackAmount += 4
        if self.stack and self.check_player_has_plus_four():
            self.stack_in_play = True
            self.wild_in_play = True
            self.draw_card_in_play = False 
            output = f"**{past_player}** has played a +4! \n Current Stack is now **+{self.stackAmount}**!\n**{self.get_current_player()}** can now choose to continue the stack or take the cards with **!draw**"
        else:
            self.stack_in_play = False
            skipped_player = self.current_player_index
            self.current_player_index = self.get_next_player_index()     
            for _ in range(self.stackAmount):
                self.hands[skipped_player].append(self.deck.draw_card())
            output = f"**{self.players[skipped_player]}** drew **{self.stackAmount}** cards and lost their turn!"
            self.stackAmount = 0
            return output
        
    def reverse_played(self) -> str:
        self.player_order.reverse()
        self.current_player_index = self.get_next_player_index()
        return f"Order has been reversed!"

    def skip_played(self, player_index) -> str:
        skipped_player = 0
        #If person who played is at end of list
        if player_index == self.player_order[-1]:
            if len(self.players) > 2:
                self.current_player_index = self.player_order[1]
                skipped_player = self.player_order[0]
            else:
                skipped_player = self.player_order[0]
        #If person who played is second to last
        elif player_index == self.player_order[-2]:
            self.current_player_index = self.player_order[0]
            skipped_player = self.player_order[-1]
        #If they were in the middle somewhere
        else:
            self.current_player_index = self.player_order[self.player_order.index(player_index) + 2]
            skipped_player = self.player_order[self.player_order.index(player_index) + 1]

        return f"{self.players[skipped_player]} has been skipped!"
