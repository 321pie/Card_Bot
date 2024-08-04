import Games.deck as deck

class Game():
    #Inits variables common to all games
    def __init__(self):
        self.deck:deck.Deck = deck.Deck() #The deck that the game is played with
        self.players:list[list] = [] #The master list of players (whatever the external app uses as an identifier)
        self.hands:list[list[deck.Card]] = [] #The hands of each player, indexed the same as the players
        self.end = [] #List of players who wish to prematurely end the game
        self.game_started = False #True if the game has begun, else False

    #Adds a player to the game
    #Returns True on success, False on failure
    def add_player(self, player) -> bool:
        if player not in self.players:
            self.players.append(player)
            return True
        else:
            return False
        
    #Removes a player from the game
    #Returns True on success, False on failure
    def remove_player(self, player) -> bool:
        if player in self.players:
            self.players.remove(player)
            return True
        else:
            return False
        
    #Returns and removes card at given index
    #Returns card on success, False on failure
    def card_select(self, player, index:int) -> bool | deck.Card:
        try:
            player_index = self.players.index(player)
        except:
            return False
        
        if (index >= len(self.hands[player_index])) or (index < 0):
            return False
        else:
            self.process_card_select(player_index, index)
            return self.hands[player_index].pop(index)
        
    #Gets the specified player's hand
    #Returns hand on success, False on failure
    def get_hand(self, player) -> bool | list[deck.Card]:
        try:
            player_index = self.players.index(player)
        except:
            return False
        
        return self.hands[player_index]
    
    #Create hands of the specified size
    #Returns True on success, False on failure
    def create_hands(self, hand_size:int) -> bool:
        self.deck.reset_deck()

        self.hands = self.deck.get_hands(len(self.players), hand_size)

        if len(self.hands) == 0:
            return False
        
        return True
    
    #Starts the game
    #Returns True on success, False on failure
    def start_game(self):
        if len(self.players) == 0:
            return False
        if self.game_started == True:
            return False
        elif self.initialize_game() == False:
            return False
        else:
            self.game_started = True

        return True
    
###############################################################################
# List of common functions that must be implemented
###############################################################################
    #Initializes the game on start
    #Returns 0 on success, -1 on failure
    def initialize_game(self) -> bool:
        return False
    
###############################################################################
# List of common functions that may be implemented
###############################################################################
    #Optionally used to modify variables on card select
    #NOTE: Card gets deleted, so don't modify self.hands. See self.card_select() for more details.
    def process_card_select(self, player_index:int, card_index:int):
        pass