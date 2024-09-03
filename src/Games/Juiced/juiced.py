import copy

from Games.game import Game
import Games.Juiced.juiced_deck as deck
from Games.deck import Card

class Juiced(Game):
    #Inits variables common to all games
    def __init__(self):
        super().__init__()
        self.deck:deck.White_Deck = deck.White_Deck() #The deck that holds the players' cards
        self.judge_deck:deck.Black_Deck = deck.Black_Deck() #The deck that holds the cards that the judge wields
        self.min_player_count:int = 3 #Defines the minimum number of players that have to !join before the game cans start
        self.max_player_count:int = 16 #Defines the maximum number of players
        self.judge_index:int = 0 #Index of the current judge
        self.judge_card:Card = None
        self.judging:bool = False #Determines whether or not we are in the judging phase
        self.unholy_actions:list = [] #List to hold the cards that players have thrown to be judged
        self.points:list[int] = [] #List to hold point totals (indexed same as players)
        self.win_points:int = 6 #Number of points needed to win a game

    #Initializes the game on start
    #Returns True on success, False on failure
    def initialize_game(self) -> bool:
        #Variable declared in base class
        self.hands = self.deck.get_hands(len(self.players), 10)

        for _ in self.players:
            self.points.append(0)
            self.unholy_actions.append(None)
        
        self.judge_card = self.judge_deck.get_card()

    #Optionally used to modify variables on card select
    #card_index needs to be indexed based on: (judge -> self.unholy_actions) (player -> self.hands[player_index])
    #NOTE: Card gets deleted, so don't modify self.hands. See self.card_select() for more details.
    def process_card_select(self, player_index:int, card_index:int) -> bool:
        #Judge can't play during unholy actions, and players can't play while Judge Judy is going at it
        if self.judging:
            if player_index != self.judge_index:
                return False
            if card_index == self.judge_index:
                return False
            #Add proxy that will get deleted, assign a new Judge Judy, and give a point
            self.hands[self.judge_index].insert(card_index, None)
            self.judge_index = card_index
            self.points[card_index] += 1

            self.reset_round()
        else:
            #If Judge Judy is disrespecting the rules of the courtroom or the player has already played
            if (player_index == self.judge_index) or (self.unholy_actions[player_index] != None):
                return False
            
            #Add card to be judged and add new card to the player's hand
            self.unholy_actions[player_index] = copy.copy(self.hands[player_index][card_index])
            self.hands[player_index].append(self.deck.get_card())

            #Check to see if it's judging time
            if self.unholy_actions.count(self.unholy_actions[0]) == (len(self.unholy_actions)-1):
                self.judging = True

        return True
    
    #Prepare for new round. Returns player that won if game has ended, else None
    def reset_round(self):
        self.judging = False
        self.judge_card = self.judge_deck.get_card()

        #Reset deck if low
        if self.deck.get_length() < len(self.players) + 10:
            self.deck.reset_deck()
        if self.judge_deck.get_length() < len(self.players) + 10:
            self.judge_deck.reset_deck()

        for player_index in range(len(self.players)):
            self.unholy_actions[player_index] = None
            if self.points[player_index] >= self.win_points:
                self.end_game()
                return self.players[player_index]
            
        return None
    
    #Get a list of cards that players have played to be judged
    def get_unholy_actions(self) -> list:
        return copy.copy(self.unholy_actions)
    
    #Returns player that is winning if always_return==True, else will return None if a winner is not found
    def get_winner(self, always_return=False):
        winner_index = 0
        points = 0
        for player_index in range(len(self.players)):
            if self.points[player_index] > points:
                winner_index = player_index
                points = self.points[player_index]

        if (always_return == False) and (points < self.win_points):
            return None
        
        return self.players[winner_index]
    
    #Returns self.points if no player specified, else player's points or None if player doesn't exist
    def get_points(self, player=None):
        if player == None:
            return copy.copy(self.points)
        else:
            if player in self.players:
                return self.points[self.players.index(player)]
            
        return None
    
    #Gets the current judge
    def get_judge(self):
        return self.players[self.judge_index]
    
    #Gets the current judge card
    def get_judge_card(self):
        return self.judge_card