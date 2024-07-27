import deck
import game

class Cribbage(game.Game):
    def __init__(self):
        super().__init__()

        self.points = [] #Number of points, indexed same as players
        self.backup_hands = [] #Hands that always have hand_size cards, indexed same as players
        self.thrown_cards = [] #Cards that each player has thrown away, indexed same as players
        self.crib = [] #Crib cards
        
        self.num_thrown = [] #Number of cards thrown in crib, indexed same as players
        self.pegging_list = [] #List of cards in pegging round
        self.point_goal = 121 #Number of points to win
        self.skunk_length = 30 #Number of points from skunk line to end -1
        self.crib_count = 4 #Number of cards in crib
        self.hand_size = 4 #Number of cards in a hand after throwing to crib
        self.crib_index = 0 #crib_index++ each round. Crib belongs to players[crib_index%len(players)]
        self.pegging_index = 0 #(crib_index + 1) % len(players)
        self.throw_count = 0 #How many cards each player throws, initialized upon starting game
        self.throw_away_phase = False #True if players still need to throw cards away
        self.pegging_phase = False #True if players are in the pegging phase
        self.calc_string = "" #Saves most recent hand calculations
        self.team_count = 1 #Variable to hold number of players per team (combine points)