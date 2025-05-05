#Foreign imports
from copy import copy
from random import shuffle

HEART = ':heart_suit:' #'♥'
DIAMOND = ':diamond_suit:' #'♦'
CLUB = ':club_suit:' #'♣'
SPADE = ':spade_suit:' #'♠'

ACE = 'A'
JACK = 'J'
QUEEN = 'Q'
KING = 'K'
JOKER = ':joker:'

RED = ':red_circle:'
BLACK = ':black_large_square:'

VALUES = [ACE, '2', '3', '4', '5', '6', '7', '8', '9', '10', JACK, QUEEN, KING]
SUITS = [HEART, DIAMOND, CLUB, SPADE]

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def to_int_runs(self):
        if self.value == ACE :
            return 1
        elif self.value == JACK:
            return 11
        elif self.value == QUEEN:
            return 12
        elif self.value == KING:
            return 13
        elif self.value == JOKER:
            return -1
        else:
            return int(self.value)
        
    def to_int_15s(self):
        if self.value == ACE:
            return 1
        elif self.value in [JACK, QUEEN, KING]:
            return 10
        elif self.value == JOKER:
            return -1
        else:
            return int(self.value)
        
    def display(self):
        return f'{self.value} {self.suit}'

class Deck:
    def __init__(self):
        self.reset_deck()
        
    def reset_deck(self):
        self.deck:list[Card] = []
        self.flipped:Card = None #Card that gets flipped after throwing cards away

        for suit in SUITS:
            for value in VALUES:
                self.deck.append(Card(value, suit))

        shuffle(self.deck)

    def get_hands(self, num_hands, num_cards):
        #Check that values are within bounds
        hands = []
        if num_hands*num_cards <= len(self.deck):
            for h in range(num_hands):
                hand = []
                for c in range(num_cards):
                    hand.append(self.deck[0])
                    del self.deck[0]
                hands.append(hand)
        
        return hands
    
    #Gets a card, deletes it from the deck, but stores it in deck.flipped
    def get_flipped(self):
        if (self.flipped == None) and (not self.is_empty()):
            self.flipped = self.deck[0]
            del self.deck[0]

        return self.flipped
    
    #Gets a card, deleting it froom the deck
    def get_card(self):
        if (not self.is_empty()):
            extra = self.deck[0]
            del self.deck[0]

            return extra
        return None
    
    def get_length(self):
        return len(self.deck)
    
    def is_empty(self):
        if(len(self.deck) <= 0):
            return True
        else:
            return False
        
    def get_deck(self):
        return copy(self.deck)
    
    def set_deck(self, cards:list[Card]):
        self.deck = copy(cards)
    
class JokerDeck(Deck):
    def reset_deck(self):
        super().reset_deck()
        self.deck.append(Card(JOKER, RED))
        self.deck.append(Card(JOKER, BLACK))

class Peasant_Deck(Deck):
    def reset_deck(self):
        super().reset_deck()
        self.deck = [card for card in self.deck if card.value not in [JACK, QUEEN, KING]]

class Royal_Deck(Deck):
    def reset_deck(self):
        super().reset_deck()
        self.deck = [card for card in self.deck if card.value in [JACK, QUEEN, KING]]