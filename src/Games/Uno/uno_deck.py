#Foreign imports
from random import randint

COLORS = ['red', 'yellow', 'green', 'blue']
NUMBER_CARDS = ['0', '1', '2', '3', '4','5', '6', '7', '8', '9']
ACTION_CARDS = ['skip', 'reverse', 'draw2']
WILD_CARDS = ['wild', 'wild4']

class Card:
    def __init__(self, value, color):
        self.value = value
        self.color = color
    
    def to_int_runs(self):
        if (self.value == "skip"):
            return 9
        elif(self.value == "reverse"):
            return 10
        elif(self.value == "draw2"):
            return 11
        elif(self.value == "wild"):
            return 4
        elif(self.value == "wild4"):
            return 8
        elif (self.value == '0'):
            if self.color == "red":
                return 1
            elif self.color == "blue":
                return 0
            elif self.color == "yellow":
                return 2
            elif self.color == "green":
                return 3
        else:
            return int(self.value)
        
    def display(self):
        return f'{self.value} {self.color}'

class Deck:
    def __init__(self):
        for color in COLORS:
            for number in NUMBER_CARDS:
                self.deck.append(Card(number, color))
            for action in ACTION_CARDS:
                self.deck.append(Card(action, color))
            for wild in WILD_CARDS:
                self.deck.append(Card(wild, color))

    def get_hands(self, num_hands):
        # Infinite number of cards in uno deck
        hands = []
        for i in range(num_hands):
            hand = []
            for j in range(7):
                hand.append(self.deck[randint(0, len(self.deck)-1)])
            hands.append(hand)

        return hands
    
    def get_start(self):
        # Minus 21 to avoid starting with wild/action cards
        return self.deck[randint(0, len(self.deck)-21)]
    
    def draw_card(self, hand, target):
        return self.deck(randint(0, len(self.deck)-1))