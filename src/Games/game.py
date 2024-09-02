import copy
import Games.deck as deck

class Game():
    #Inits variables common to all games
    def __init__(self):
        self.deck:deck.Deck = deck.Deck() #The deck that the game is played with
        self.players:list = [] #The master list of players (whatever the external app uses as an identifier)
        self.hands:list[list[deck.Card]] = [] #The hands of each player, indexed the same as the players
        self.game_started:bool = False #True if the game has begun, else False
        self.min_player_count:int = 1 #Defines the minimum number of players that have to !join before the game cans start
        self.max_player_count:int = 8 #Defines the maximum number of players

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
    def card_select(self, player, card_index:int) -> bool | deck.Card:
        if player in self.players:
            player_index = self.players.index(player)
            if (card_index < len(self.hands[player_index])) and (card_index >= 0):
                self.process_card_select(player_index, card_index)
                return self.hands[player_index].pop(card_index)
            
        return False
        
    #Gets the specified player's hand
    #Returns hand on success, None on failure
    def get_hand(self, player) -> None | list[deck.Card]:
        try:
            player_index = self.players.index(player)
        except:
            return None
        
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
        if (len(self.players) < self.min_player_count) or (len(self.players) > self.max_player_count):
            return False
        if self.game_started == True:
            return False
        elif self.initialize_game() == False:
            return False
        else:
            self.game_started = True

        return True
    
    #Ends the game
    #Returns True on success, False on failure
    def end_game(self):
        self.game_started = False

        return True

    #Returns the player list
    def get_players(self):
        return copy.copy(self.players)
    
    #Returns the index of the player or None if the player doesn't exist
    def get_player_index(self, player):
        try:
            return self.players.index(player)
        except:
            return None
        
    #Returns the hand of the specified player (index or name)
    def get_player_hand(self, player_index=None, player=None):
        #Get based on index
        if (player_index != None) and (player_index in range(len(self.players))):
            return self.hands[player_index]

        #Get based on player
        if (player != None) and (player in self.players):
            return self.hands[self.players.index(player)]
        
    #Returns all hands
    def get_hands(self) -> list[list[deck.Card]]:
        return copy.copy(self.hands)
    
###############################################################################
# List of common functions that must be implemented
###############################################################################
    #Initializes the game on start
    #Returns True on success, False on failure
    def initialize_game(self) -> bool:
        return False
    
###############################################################################
# List of common functions that may be implemented
###############################################################################
    #Optionally used to modify variables on card select
    #NOTE: Card gets deleted, so don't modify self.hands. See self.card_select() for more details.
    def process_card_select(self, player_index:int, card_index:int) -> bool:
        False