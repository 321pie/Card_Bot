import deck

class Game():
    #Inits variables common to all games
    def __init__(self):
        self.deck:deck.Deck = deck.Deck() #The deck that the game is played with
        self.players:list[list] = [] #The master list of players (whatever the external app uses as an identifier)
        self.hands:list[list[deck.Card]] = [] #The hands of each player, indexed the same as the players
        self.end = [] #List of players who wish to prematurely end the game
        self.game_started = False #True if the game has begun, else False

    #Adds a player to the game
    #Returns 0 on success, -1 on failure
    def add_player(self, player) -> int:
        if player not in self.players:
            self.players.append(player)
            return 0
        else:
            return -1
        
    #Returns and removes card at given index
    #Returns 0 on success, -1 on failure
    def card_select(self, player, index:int) -> int | deck.Card:
        try:
            player_index = self.players.index(player)
        except:
            return -1
        
        if (index >= len(self.hands[player_index])) or (index < 0):
            return -1
        else:
            return self.hands[player_index].pop(index)
        
    #Gets the specified player's hand
    #Returns 0 on success, -1 on failure
    def get_hand(self, player) -> int | list[deck.Card]:
        try:
            player_index = self.players.index(player)
        except:
            return -1
        
        return self.hands[player_index]
    
    #Create hands of the specified size
    #Returns 0 on success, -1 on failure
    def create_hands(self, hand_size:int):
        self.deck.reset_deck()

        self.hands = self.deck.get_hands(len(self.players), hand_size)

        if len(self.hands) == 0:
            return -1
        
        return 0
    
    #Starts the game
    #Returns 0 on success, -1 on failure
    def start_game(self):
        if len(self.players) == 0:
            return -1
        elif self.initialize_game() == -1:
            return -1
        else:
            self.game_started = True

        return 0
    
###############################################################################
# List of common functions that must be implemented
###############################################################################
    #Initializes the game on start
    #Returns 0 on success, -1 on failure
    def initialize_game(self) -> int:
        return -1