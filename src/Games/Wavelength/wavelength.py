import copy
from random import randint

from Games.game import Game
import Games.Wavelength.wavelength_deck as deck
from Games.deck import Card

class Wavelength(Game):
    #Inits variables common to all games
    def __init__(self):
        super().__init__()
        self.deck:deck.Spectrum_Deck = deck.Spectrum_Deck() #The deck that holds the available cards
        self.min_player_count:int = 2 #Defines the minimum number of players that have to !join before the game can start
        self.max_player_count:int = 16 #Defines the maximum number of players
        self.judge_index:int = 0 #Index of the person who describes, NOT guess
        self.judge_card:Card = None #The card that players choose on the scale
        self.correct_answer:int = 0 #The correct answer from lowest_guess to highest_guess
        self.lowest_guess:int = -10 #Lowest possible guess
        self.highest_guess:int = 10 #Highest possible guess
        self.guess_list:list[list[int]] = [] #List to hold the values that payers have guessed
        self.points:list[int] = [] #List to hold point totals (indexed same as players)
        self.win_points:int = 20 #Number of points needed to win a game

    #Initializes the game on start
    #Returns True on success, False on failure
    def initialize_game(self) -> bool:
        #Reinitialize with updated values for available cards, adding defaults if none are initialized
        self.deck = deck.Spectrum_Deck()
        if len(self.deck.get_deck()) < 10:
            deck.spectrum_cards += deck.DEFAULT_CARDS
            self.deck = deck.Spectrum_Deck()

        self.reset_round()

    #If round ended, returns True or winner's name. Else, returns False.
    def process_guess(self, player:any, guess:int) -> bool:
        player_index = self.players.index(player)

        #Player who knows the correct answer can't vote
        if player_index == self.judge_index:
            return False
        
        #Must be a valid guess
        if not self.lowest_guess <= guess <= self.highest_guess:
            return False
        
        self.guess_list[player_index] = guess

        #If everyone except judge has guessed, then assign a new judge, calc points, and move on to next round.
        if len([gess for gess in self.guess_list if gess != None]) == len(self.players) - 1:
            self.judge_index = (self.judge_index + 1) % len(self.players)

            for player_index in range(len(self.players)):
                if self.guess_list[player_index] != None:
                    self.points[player_index] += self.calc_points(self.guess_list[player_index])

            self.reset_round()

            return True

        return False

    # #Optionally used to modify variables on card select
    # #card_index needs to be indexed based on: (judge -> self.unholy_actions) (player -> self.hands[player_index])
    # #NOTE: Card gets deleted, so don't modify self.hands. See self.card_select() for more details.
    # def process_card_select(self, player_index:int, card_index:int) -> bool:
    #     if player_index == self.judge_index:
    #         return False
    #     if card_index == self.judge_index:
    #         return False
            
    #     #Assign a new Judge Judy, give points, and reset round
    #     self.judge_index = (self.judge_index + 1) % len(self.players)

    #     for player_index in range(len(self.players)):
    #         add_points = self.calc_points()
    #         self.points[player_index] += add_points
    #         self.points[self.judge_index] += add_points
        
    #     self.reset_round()

    #     return False
    
    #Prepare for new round. Returns player that won if game has ended, else None
    def reset_round(self):
        #Init variables to initialize the game
        self.hands = [] #No hands!
        for _ in self.players:
            self.points.append(0)
            self.guess_list.append(None)
        
        #Set up category and correct answer
        self.judge_card = self.deck.get_card()
        self.correct_answer = randint(self.lowest_guess, self.highest_guess)

        #Reset deck if low (chose 5 for no particular reason)
        if (self.deck.get_length() < 5):
            self.deck.reset_deck()

        for player_index in range(len(self.players)):
            self.guess_list[player_index] = None
            if self.points[player_index] >= self.win_points:
                self.end_game()
                deck.spectrum_cards = []
                return self.players[player_index]
            
        return None
    
    #Calculates the number of points given a guess and using self.correct_answer
    def calc_points(self, guess:int) -> int:
        #See if within 2. Worth 4 if exact, 3 if one off, and 2 if two off. Else worth 0.
        points = abs(guess - self.correct_answer)
        if points > 2:
            return 0
        else:
            return abs(points - 2) + 2
    
    #Get a list of cards that players have played to be judged
    def did_guess(self, player) -> bool:
        if player not in self.players:
            return False
        else:
            return self.guess_list[self.players.index(player)] != None
    
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