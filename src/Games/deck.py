#Foreign imports
from random import randint

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
        if(self.value == ACE):
            return 1
        elif(self.value == JACK):
            return 11
        elif(self.value == QUEEN):
            return 12
        elif(self.value == KING):
            return 13
        elif(self.value == JOKER):
            return -1
        else:
            return int(self.value)
        
    def to_int_15s(self):
        if(self.value == ACE):
            return 1
        elif(self.value in [JACK, QUEEN, KING]):
            return 10
        elif(self.value == JOKER):
            return -1
        else:
            return int(self.value)
        
    def display(self):
        return f'{self.value} {self.suit}'

class Deck:
    def __init__(self):
        self.reset_deck()
        
    def reset_deck(self):
        self.deck = []
        self.flipped = None #Card that gets flipped after throwing cards away

        for suit in SUITS:
            for value in VALUES:
                self.deck.append(Card(value, suit))

    def get_hands(self, num_hands, num_cards):
        #Check that values are within bounds
        hands = []
        if(num_hands * num_cards <= len(self.deck)):
            for h in range(num_hands):
                hand = []
                for c in range(num_cards):
                    card = randint(0, len(self.deck)-1)
                    hand.append(self.deck[card])
                    del self.deck[card]
                hands.append(hand)
        
        return hands
    
    def get_flipped(self):
        if(self.flipped == None and len(self.deck) >= 1):
            card = randint(0, len(self.deck)-1)
            self.flipped = self.deck[card]
            del self.deck[card]

        return self.flipped
    
    def get_card(self):
        if(len(self.deck) >= 1):
            card = randint(0, len(self.deck)-1)
            extra = self.deck[card]
            del self.deck[card]

            return extra
        return None
    
class JokerDeck(Deck):
    def reset_deck(self):
        super().reset_deck()
        self.deck.append(Card(JOKER, RED))
        self.deck.append(Card(JOKER, BLACK))