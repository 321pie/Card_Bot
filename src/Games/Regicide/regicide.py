from Games.game import Game
import Games.deck as deck
from Games.deck import Card
from copy import copy
from random import shuffle

class Regicide(Game):
    #Inits variables common to all games
    def __init__(self):
        super().__init__()
        self.JACK_ATK = 10
        self.JACK_HP = 20
        self.QUEEN_ATK = 15
        self.QUEEN_HP = 30
        self.KING_ATK = 20
        self.KING_HP = 40

        self.deck:deck.Peasant_Deck = deck.Peasant_Deck() #The deck that holds the players' cards
        self.royal_deck:deck.Royal_Deck = deck.Royal_Deck() #The deck that holds the cards you fight
        self.min_player_count:int = 1 #Defines the minimum number of players that have to !join before the game can start
        self.max_player_count:int = 4 #Defines the maximum number of players
        self.hand_len = 8 #Length of hands
        self.cur_royal:Card = None #Current enemy you're fighting
        self.royal_hp = 0 #cur_royal's current hp
        self.royal_atk = 0 #cur_royal's current attack
        self.cur_player_index = 0 #Index of the current player's turn
        self.cur_atk_def:list[Card] = [] #Collection of cards in current turn's attack/defense against the royal
        self.discard:list[Card] = [] #Shared discard pile
        self.defending = False #Boolean to denote whether players are attacking or defending
        self.yield_count = 0 #Number of times players have yielded in a row
        self.jester_attack_reduction = 0 #Sum of spades played on immune enemies (works retroactively on jester activation)
        self.jester_count = 2 #Number of jesters (jokers) that can still be used
        self.jester_active = False #Denotes whether a jester (joker) is actiely removing immunity

    #Initializes the game on start
    #Returns True on success, False on failure
    def initialize_game(self) -> bool:
        #Init variables to initialize the game
        self.hands = self.deck.get_hands(len(self.players), self.hand_len) #Variable declared in base class

        #Sort and shuffle royal deck for random jacks then random queens then random kings
        temp_deck = self.royal_deck.get_deck()
        temp_deck.sort(key=lambda x: x.to_int_runs())
        jacks = temp_deck[:4]
        queens = temp_deck[4:8]
        kings = temp_deck[8:]
        shuffle(jacks)
        shuffle(queens)
        shuffle(kings)
        self.royal_deck.set_deck(jacks + queens + kings)

        #Init cur_royal
        self.committed_regicide()

    #Optionally used to modify variables on card select
    #NOTE: Card gets deleted, so don't modify self.hands. See self.card_select() for more details.
    def process_card_select(self, player_index:int, card_index:int) -> bool:
        #Make sure that the right person is playing a card
        if player_index != self.cur_player_index:
            return False
        
        #Verify that the current card can be played and add to cur_atk
        card = self.hands[self.cur_player_index][card_index]
        if (self.defending or \
        len(self.cur_atk_def) == 0) or \
        (len([tarjeta for tarjeta in self.cur_atk_def if tarjeta.value == card.value or tarjeta.value == deck.ACE]) == len(self.cur_atk_def) and sum([self.get_card_power(tarjeta) for tarjeta in self.cur_atk_def if tarjeta.value == card.value]) + card.to_int_15s() <= 10) or \
        (card.value == deck.ACE or self.cur_atk_def[0].value == deck.ACE):
            self.cur_atk_def.append(card)
        else:
            return False

        return True
    
    #Executes attack/defense if able
    def execute(self, player):
        if player != self.get_cur_player():
            return False
        if self.defending == True:
            if sum([self.get_card_power(card) for card in self.cur_atk_def]) < self.royal_atk:
                if sum([self.get_card_power(card) for card in self.hands[self.players.index(player)]]) >= self.royal_atk:
                    return False #If you can defend, you must
                else:
                    self.end_game()
                
            self.cur_player_index = (self.cur_player_index+1) % len(self.players)
            self.defending = False
            self.cur_atk_def = []
        else:
            if len(self.cur_atk_def) == 0:
                return False #Can't attack with nothing. Must yield instead
            
            power = self.calculate_power()

            #If red, resolve power
            if any([(card.suit == deck.HEART) for card in self.cur_atk_def]) and (self.cur_royal.suit != deck.HEART or self.jester_active): #Shuffle discard, select (# on card) cards and put them on bottom of deck
                shuffle(self.discard)
                if len(self.discard) < power:
                    self.deck.set_deck(self.deck.get_deck() + self.discard)
                else:
                    self.deck.set_deck(self.deck.get_deck() + self.discard[:power])
            if any([(card.suit == deck.DIAMOND) for card in self.cur_atk_def]) and (self.cur_royal.suit != deck.DIAMOND or self.jester_active): #Starting with cur_player, all players draw one until (# on card) cards have been drawn
                self.draw_cards(power)
            
            #Add in black powers
            if any([(card.suit == deck.CLUB) for card in self.cur_atk_def]) and (self.cur_royal.suit != deck.CLUB or self.jester_active): #Double the power
                power *= 2
            if any([(card.suit == deck.SPADE) for card in self.cur_atk_def]):
                if self.cur_royal.suit != deck.SPADE or self.jester_active: #Permanently reduce cur_royal's attack
                    self.royal_atk -= power
                    if self.royal_atk < 0:
                        self.royal_atk = 0
                else:
                    self.jester_attack_reduction += power

            #Damage royal and see if it died
            self.royal_hp -= power
            if self.royal_hp == 0:
                self.deck.set_deck([self.cur_royal] + self.deck.get_deck())
                self.committed_regicide()
                self.cur_player_index = (self.cur_player_index+1) % len(self.players)
            elif self.royal_hp < 0:
                self.discard.append(self.cur_royal)
                self.committed_regicide()
                self.cur_player_index = (self.cur_player_index+1) % len(self.players)
            else:
                #If we didn't kill the royal, then time for damage phase
                self.defending = True

            #Reset played cards and yield count
            self.cur_atk_def = []
            self.yield_count = 0

        return True

    #Yields turn and returns True if able, else returns False
    def yield_turn(self, player):
        if (player == self.players[self.cur_player_index]) and (len(self.cur_atk_def) == 0) and (self.yield_count < len(self.players)-1):
            self.yield_count += 1
            self.defending = True

            return True
        
        return False

    #Activates jester (joker) and returns True if able, else returns False
    def jester(self, player):
        if (player == self.players[self.cur_player_index]) and (len(self.cur_atk_def) == 0) and (self.jester_count > 0):
            if len(self.players) > 1:
                self.royal_atk -= self.jester_attack_reduction
                self.jester_attack_reduction = 0
                self.jester_active = True
            else:
                self.hands = self.deck.get_hands(len(self.players), self.hand_len)
                
            self.jester_count -= 1
    
    #Get next royal and decide if game is won. Returns True if game is won, else returns false
    def committed_regicide(self):
        self.jester_attack_reduction = 0
        self.jester_active = False
        if not self.royal_deck.is_empty():
            #Get first card
            self.cur_royal = self.royal_deck.get_card()
            
            if self.cur_royal.value == deck.JACK:
                self.royal_atk = self.JACK_ATK
                self.royal_hp = self.JACK_HP
            elif self.cur_royal.value == deck.QUEEN:
                self.royal_atk = self.QUEEN_ATK
                self.royal_hp = self.QUEEN_HP
            elif self.cur_royal.value == deck.KING:
                self.royal_atk = self.KING_ATK
                self.royal_hp = self.KING_HP

            return False
        else:
            self.end_game()
            return True
    
    #Get a list of cards that players have played for the current attack/defense
    def get_cur_atk_def(self) -> list:
        return copy(self.cur_atk_def)
    
    #Gets the player whose turn it is
    def get_cur_player(self):
        return self.players[self.cur_player_index]
    
    #Gets the current foe
    def get_cur_royal(self):
        return self.cur_royal
    
    #Returns the value of the card (1-10, 15, 20)
    def get_card_power(self, card:Card) -> int:
        card_power = card.to_int_runs()
        if card.to_int_runs() > 10:
            if card.value == deck.JACK:
                card_power = self.JACK_ATK
            elif card.value == deck.QUEEN:
                card_power = self.QUEEN_ATK
            elif card.value == deck.KING:
                card_power = self.KING_ATK

        return card_power
    
    #Each player draws a card for draw_number of cards unless they have max hand size
    def draw_cards(self, draw_number):
        ii = 0
        while draw_number > 0:
            if self.deck.is_empty():
                break

            #If current player, check if current hand is greater than or equal to hand_len + 1. Elif check if current hand is >= hand_len
            #If so, check if any player can draw. If not, break. Else, skip player
            if self.cur_player_index == (self.cur_player_index + ii) % len(self.hands):
                if len(self.hands[(self.cur_player_index + ii) % len(self.hands)]) >= self.hand_len + 1:
                    if len([hand for hand in self.hands if len(hand) >= self.hand_len]) >= len(self.hands):
                        break
                    ii += 1
                    continue
            elif len(self.hands[(self.cur_player_index + ii) % len(self.hands)]) >= self.hand_len:
                if len([hand for hand in self.hands if len(hand) >= self.hand_len]) >= len(self.hands):
                    break
                ii += 1
                continue

            #GDraw a card and continue draw cycle
            self.hands[(self.cur_player_index + ii) % len(self.hands)].append(self.deck.get_card())
            ii += 1
            draw_number -= 1

    #Calulate the value of the attack/defense (without powers)
    def calculate_power(self):
        power = 0

        #Add each card's power to the total
        for card in self.cur_atk_def:
            power += self.get_card_power(card)

        return power
    
    #Returns the total power of cur_atk_def
    def get_current_total(self):
        power = self.calculate_power()

        if not self.defending:
            #Add in black powers
            for card in self.cur_atk_def:
                if card.suit == deck.CLUB and (self.cur_royal.suit != deck.CLUB or self.jester_active): #Double the power
                    power *= 2

        return power

    #Used to change whose turn it is (for jester) and return True. if player not in self.players, then return False
    def change_cur_player(self, player):
        try:
            self.cur_player_index = self.players.index(player)

            return True
        except:
            return False
        
    def get_royal_hp(self):
        return self.royal_hp
    
    def get_royal_atk(self):
        return self.royal_atk