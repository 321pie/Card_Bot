from math import factorial, floor
from random import random
from typing import List

from Games.Uno.uno_deck import Card
from Games.Uno.uno_deck import Deck
import Games.game as game
from Games.Uno.uno_print import Uno_Print


class Uno(game.Game):
    def __init__(self):
        super().__init__()
        self.deck = Deck()
        self.hands:list[list[Card]] = [] #The hands of each player, indexed the same as the players
        self.top_card: Card #Card to start with and what everyone will play off of
        self.player_order: List[int] = [] # Player order list with player indexes as values
        self.current_player_index: int = 0 # Index of player whose turn it is to play
        self.wild_in_play: bool = False #Blocks players from playing until wild color is chosen
        self.draw_card_in_play: bool = False # Blocks players from playing until player has chosen to keep/play drawn card
        self.uno_tracker: List[bool] = [] # List to keep track of who has called uno or not. Indexed the same as players

    #Initializes the game on start
    #Returns 0 on success, -1 on failure
    def initialize_game(self) -> bool:
        self.player_order = random.shuffle(list(len(self.players)))
        self.current_player_index = self.player_order[0]
        self.top_card = self.deck.get_start()
        
        #Get initial Player hands
        self.hands = self.deck.get_hands(len(self.players))
        return True

    #Returns a player that won or None if no winner
    def get_winner(self):
        point_array = self.points

        if self.team_count != 1:
            point_array = self.get_point_array()

        for player_index in range(len(point_array)):
            if(point_array[player_index] >= self.point_goal):
                return self.players[player_index]

        return None
    

    def process_card_select(self, player_index:int, card_index:int) -> str:
        output = []
        #Check if player played their last card
        if len(self.hands[player_index]) == 0:
            self.end_game()
            return f"{self.players[player_index]} has played their last card and won the game!"

        if "wild" not in self.top_card.value:
            if self.top_card.value == "skip":
                skipped_player = 0
                if player_index == self.player_order[-1]:
                    self.current_player_index = self.player_order[1]
                    skipped_player = self.player_order[0]
                elif player_index == self.player_order[-2]:
                    self.current_player_index = self.player_order[0]
                    skipped_player = self.player_order[-1]
                else:
                    self.current_player_index = self.player_order[self.player_order.index(player_index) + 2]
                    skipped_player = self.player_order[self.player_order.index(player_index) + 1]
                output = f"{self.players[skipped_player]} has been skipped!"

            elif self.top_card.value == "reverse":
                self.player_order.reverse()
                self.current_player_index = self.get_next_player_index()
                output = f"Order has been reversed!"

            elif self.top_card.value == "draw2":
                # Calling next twice here as draw two skips your turn
                self.current_player_index = self.get_next_player_index()
                skipped_player = self.players[self.current_player_index]
                self.current_player_index = self.get_next_player_index()
                
                for _ in range(2):
                    self.hands[self.current_player_index].append(Deck.draw_card())
                output=f"{self.players[skipped_player]} drew 2 cards and lost their turn!"

            else:
                self.current_player_index = self.get_next_player_index()
                
            if self.check_player_has_usable_card() is False:
                #If someone has declared uno draws cards, their uno declaration gets reset
                if len(self.hands[self.current_player_index]) == 1:
                    self.uno_tracker[self.current_player_index] = False

                return f"{output}\n{self.draw_cards_til_matching()}"
            else:
                return f"{output}.\n{Uno_Print.get_start_string()}"
        else:
            self.wild_in_play = True
            return f"Wild card has been played! {self.get_current_player()} gets to choose what color it becomes."

    def get_current_player(self):
        return self.players[self.get_current_player_index]
    
    def get_next_player_index(self):
        if self.current_player_index == self.player_order[-1]:
            return self.player_order[0]
        else:
            return self.player_order[self.player_order.index(self.current_player_index) + 1]
        
    #This function will draw cards from the deck until you pull a wild or a card that matches color/value
    def draw_cards_til_matching(self):
        card = Deck.draw_card()
        self.hands[self.current_player_index].append(card)
        count = 1
        while(card.color != self.top_card.color or card.value != self.top_card.value or "wild" in card.value):
            card = Deck.draw_card()
            self.hands[self.current_player_index].append(card)
            count += 1
        
        self.draw_card_in_play = True
        return f"{self.players[self.current_player_index]} had no cards they could play or they choose to draw cards for some reason! They drew {count} cards.\n {self.players[self.current_player_index]} can now choose whether to !play or !keep the usable card."
    
    def check_player_has_usable_card(self) -> bool:
        hand = self.hands[self.current_player_index]
        found = False

        for i in range(len(hand)):
            if hand[i].color == self.top_card.color or hand[i].value == self.top_card.value:
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


