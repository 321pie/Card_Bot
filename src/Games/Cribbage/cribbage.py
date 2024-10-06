import copy
from math import factorial, floor

from Games.deck import Card
import Games.deck as deck
import Games.game as game

class Cribbage(game.Game):
    def __init__(self):
        super().__init__()

        self.points:list[int] = [] #Number of points, indexed same as players
        self.backup_hands:list[list[deck.Card]] = [] #Hands that always have hand_size cards, indexed same as players
        self.thrown_cards:list[deck.Card] = [] #Cards that each player has thrown away, indexed same as players
        self.crib:list[deck.Card] = [] #Crib cards
        
        self.num_thrown:list[int] = [] #Number of cards thrown in crib, indexed same as players
        self.pegging_list:list[deck.Card] = [] #List of cards in pegging round
        self.point_goal:int = 121 #Number of points to win
        self.skunk_length:int = 30 #Number of points from skunk line to end -1
        self.crib_count:int = 4 #Number of cards in crib
        self.hand_size:int = 4 #Number of cards in a hand after throwing to crib
        self.crib_index:int = 0 #crib_index++ each round. Crib belongs to players[crib_index%len(players)]
        self.pegging_index:int = 0 #(crib_index + 1) % len(players)
        self.throw_count:int = 0 #How many cards each player throws, initialized upon starting game
        self.throw_away_phase:bool = False #True if players still need to throw cards away
        self.pegging_phase:bool = False #True if players are in the pegging phase
        self.team_count:int = 1 #Variable to hold number of players per team (combine points)

    #Initializes the game on start
    #Returns 0 on success, -1 on failure
    def initialize_game(self) -> bool:
        match len(self.players):
            case 0:
                return False
            case _ if len(self.players) > 8:
                return False
            case 1 | 2:
                self.throw_count = 2
            case 3 | 4:
                self.throw_count = 1
            case _ if len(self.players) >= 5:
                self.throw_count = 1
                self.crib_count = 8
                self.point_goal = 241
                self.skunk_length = 60
            case _:
                return False
            
        #Change game phase
        self.throw_away_phase = True
        self.pegging_index = (self.crib_index + 1) % len(self.players)
        
        #Get hands
        self.hands = self.deck.get_hands(len(self.players), self.hand_size + self.throw_count)
        
        #Initiate player variables
        for _ in range(len(self.players)):
            self.points.append(0)
            self.num_thrown.append(0)
            self.thrown_cards.append([])

        return True

    #Checks if player can peg. True if they can, false if they can't
    def can_peg(self, hand, cur_sum) -> bool:
        #Check for basic case before iterating. Probably doesn't save time for small hands, but whatever.
        if(cur_sum <= 21 and len(hand) > 0):
            return True
        else:
            for card in hand:
                if(card.to_int_15s() + cur_sum <= 31):
                    return True
        return False

    #Returns a player that won or None if no winner
    def get_winner(self):
        point_array = self.points

        if self.team_count != 1:
            point_array = self.get_point_array()

        for player_index in range(len(point_array)):
            if(point_array[player_index] >= self.point_goal):
                return self.players[player_index]

        return None
        
    #Resets the round by changing variables
    def reset_round(self) -> None:
        self.deck.reset_deck()
        self.pegging_phase = False
        self.throw_away_phase = True
        self.pegging_list = []
        self.crib_index += 1
        self.pegging_index = (self.crib_index + 1) % len(self.players)
        self.hands = []
        self.backup_hands = []
        self.crib = []
        self.thrown_cards = [[] for _ in range(len(self.players))]

        for ii in range(len(self.num_thrown)):
            self.num_thrown[ii] = 0

        #Get hands for next round
        self.hands = self.deck.get_hands(len(self.players), self.hand_size + self.throw_count)
        self.backup_hands = []

    #Ends the game by resetting every variable to standard cribbage
    def end_game(self):
        self.players = []
        self.team_count = 1
        self.standard_mode()

    #Create teams with count number of players if able. Returns True on success and False on error.
    def create_teams(self, count):
        #Check for valid number
        if (count < 1):
            return False

        #If teams are even, set variable and return True
        if (len(self.players) % count == 0):
            self.team_count = count
            return True
        
        #If teams uneven, return False
        return False

    #Change a joker in the hand of the specified player. Returns True on success and False if no joker.
    def change_hand_joker(self, card:Card, player) -> bool:
        try:
            player_index = self.players.index(player)
        except:
            return False

        #Change joker in hand to specified card
        for card_index in range(len(self.hands[player_index])):
            if self.hands[player_index][card_index].value == deck.JOKER:
                self.hands[player_index][card_index] = card

                return True
        
        #If joker not found, return False
        return False

    #Changes joker that was flipped up. Returns True on success and False if no joker or if incorrect player.
    def change_flipped_joker(self, card:Card, player) -> bool:
        try:
            player_index = self.players.index(player)
        except:
            return False

        #If player flipped the card, if it's a joker, change flipped to specified card and initialize variables for next round
        if (self.crib_index % len(self.players)) == player_index:
            if self.deck.get_flipped().value == deck.JOKER:
                self.deck.flipped = card
                self.throw_away_phase = False
                self.pegging_phase = True

                #Calculate nibs and add points accordingly
                num_points = self.nibs(card)
                self.points[self.crib_index % len(self.players)] += num_points

                return True
                
        #If wrong player or flipped card isn't joker, return False
        return False

    #Change joker in crib. Returns True on success and False if no joker or if incorrect player.
    def change_crib_joker(self, card:Card, player) -> bool:
        try:
            player_index = self.players.index(player)
        except:
            return False
        
        #If player's crib and if crib has a joker, change to specified card
        if (self.crib_index % len(self.players)) == player_index:
            #Change joker in crib to specified card
            for card_index in range(len(self.crib)):
                if self.crib[card_index].value == deck.JOKER:
                    self.crib[card_index] = card

                    return True
        
        #If not player's crib or if crib doesn't have a joker, return False
        return False

    #Checks if there is at least one joker in someone's hand. Returns first player with a joker if there is. Else, returns None.
    def check_hand_joker(self):
        #If someone has a joker card (joker mode), return the player with a joker.
        for hand_index in range(len(self.hands)):
            for card in self.hands[hand_index]:
                if card.value == deck.JOKER:
                    return self.players[hand_index]
                
        #If no joker was found in hands, return None
        return None

    #Checks if there is a joker in the crib. Returns True if there is. Else, returns False.
    def check_crib_joker(self) -> bool:
        for card in self.crib:
            if card.value == deck.JOKER:
                return True
        
        return False

    #Optionally used to modify variables on card select
    #NOTE: Card gets deleted, so don't modify self.hands. See self.card_select() for more details.
    def process_card_select(self, player_index:int, card_index:int) -> bool:
        #Make sure player isn't throwing extra away
        if not self.is_finished_throwing(self.players[player_index]):
            #Add card to crib and remove from hand
            card = self.hands[player_index][card_index]
            self.crib.append(card)
            self.num_thrown[player_index] += 1
            self.thrown_cards[player_index].append(card)

            return True

        #If player has already thrown away enough cards, return False
        return False

    #Checks if player has thrown away enough cards. Returns True if all cards have been thrown. Else, returns False.
    def is_finished_throwing(self, player) -> bool:
        #Get player index
        try:
            player_index = self.players.index(player)
        except:
            return False

        #If player hasn't thrown enough cards away, return False.
        if self.num_thrown[player_index] < self.throw_count:
            return False

        #If player has thrown enough cards away, return True.
        return True
    
    #Checks if everyone has thrown away enough cards. Returns True if all cards have been thrown. Else, returns False.
    def everyone_is_finished_throwing(self) -> bool:
        #If any player hasn't thrown enough cards away, return False.
        for player_index in range(len(self.num_thrown)):
            if(self.num_thrown[player_index] < self.throw_count):
                return False

        #If every player has thrown enough cards away, return True.
        return True

    #Prepare variables for pegging round
    def prepare_pegging(self) -> None:
        self.backup_hands = copy.deepcopy(self.hands)
        flipped = self.deck.get_flipped()

        #Calculate nibs and add points accordingly
        num_points = self.nibs(flipped)
        self.points[self.crib_index % len(self.players)] += num_points

        #Make sure crib has proper number of cards
        while(len(self.crib) < self.crib_count):
            self.crib.append(self.deck.get_card())
        
        #Make sure variables are set up for pegging round
        if flipped.value != deck.JOKER:
            self.throw_away_phase = False
            self.pegging_phase = True

        return None

    #Resets variables for end of pegging round. Return sum of pegging_list.
    def pegging_done(self) -> int:
        #Prepare for next round
        self.pegging_phase = False
        my_sum = sum([my_card.to_int_15s() for my_card in self.pegging_list])
        self.pegging_index += 1
        self.pegging_list = []

        #Restore the siphoned hands to their former glory
        self.hands = self.backup_hands

        return my_sum

    #The given player pegs the given card and gets associated points. Returns [number of points, old pegging sum, current pegging sum, cards remaining, card played, next player] on success and None on failure.
    def peg(self, player, card_index):
        #Get player index
        try:
            main_player_index = self.players.index(player)
            card = self.hands[main_player_index][card_index]
        except:
            return None

        #Make sure it's author's turn
        if(self.players[self.pegging_index % len(self.players)] != self.players[main_player_index]):
            return None

        cur_sum = sum([my_card.to_int_15s() for my_card in self.pegging_list]) + card.to_int_15s()

        #Make sure sum <= 31
        if(cur_sum <= 31):
            #Remove card from hand, get points, and add to pegging list
            self.hands[main_player_index].remove(card)
            peg_points = self.check_points(card, self.pegging_list, cur_sum)
            self.points[main_player_index] += peg_points
            self.pegging_list.append(card)

            #Make sure that someone has a hand
            for player_index in range(len(self.players)):
                if(len(self.hands[player_index]) > 0):
                    new_sum = sum([my_card.to_int_15s() for my_card in self.pegging_list])
                    
                    #Make sure next person can play. If go, then reset.
                    for _ in range(len(self.players)):
                        self.pegging_index += 1

                        if(self.can_peg(self.hands[self.pegging_index % len(self.players)], new_sum)):
                            return [peg_points, cur_sum, new_sum, len(self.hands[main_player_index]), card, self.players[self.pegging_index % len(self.players)]]
                    
            #If nobody can peg, reset variables for next pegging iteration (up to 31)
            self.pegging_list = []
            if(cur_sum != 31):
                self.points[self.pegging_index % len(self.players)] += 1
                peg_points += 1
            self.pegging_index += 1

            #Make sure next person has a hand. If not, then increment.
            for _ in range(len(self.players)):
                if(len(self.hands[self.pegging_index % len(self.players)]) > 0):
                    #If here, return points, a new_sum of 0, and player
                    return [peg_points, cur_sum, 0, len(self.hands[main_player_index]), card, self.players[self.pegging_index % len(self.players)]]
                else:
                    self.pegging_index += 1

            #Return variables and none since no player has a hand
            return [peg_points, cur_sum, 0, len(self.hands[main_player_index]), card, None]
        
        #If player can't play that card, return None
        return None

    #Returns an array of points (formats for teams or singles as needed)
    def get_point_array(self):
        point_array = []

        point_count = 0
        num_teams = len(self.players) // self.team_count

        for team_num in range(num_teams):
            for player in range(self.team_count):
                point_count += self.points[player*num_teams + team_num]
            point_array.append(point_count)
            point_count = 0

        return point_array

    #Sets up game for standard mode
    def standard_mode(self):
        self.deck = deck.Deck()
        self.points = []
        self.hands = []
        self.backup_hands = []
        self.crib = []
        self.num_thrown = []
        self.pegging_list = []
        self.point_goal = 121
        self.skunk_length = 30
        self.crib_count = 4
        self.hand_size = 4
        self.crib_index = 0
        self.pegging_index = 0
        self.throw_count = 0
        self.game_started = False
        self.throw_away_phase = False
        self.pegging_phase = False

    #Sets up game for mega hand
    def mega_hand(self):
        if(self.game_started == False):
            self.point_goal = 241
            self.skunk_length = 60
            self.hand_size = 8

    #Sets up game for joker mode
    def joker_mode(self):
        if(self.game_started == False):
            self.deck = deck.JokerDeck()

    #Finding Nibs  
    def nibs(self, flipped):
        points = 0

        #For Nibs (flipping a jack)
        if flipped.value == deck.JACK:
            points += 2

        return points

    #Check points for counting, with cur_card NOT in old_cards, but cur_card IS included in sum
    def check_points(self, cur_card, old_cards, sum):
        points = 0
        if(len(old_cards) >= 2): #Find longest run if enough cards
            complete_run = True
            total_card_index = 2
            while(total_card_index <= len(old_cards)):
                #Populate card list for runs, starting with 3 and incrementing until run is broken or there are no more cards
                cards = [cur_card.to_int_runs()]
                for card_index in range(1, total_card_index+1):
                    cards.append(old_cards[-card_index].to_int_runs())

                #sort cards to determine run and increment total_card_index for next iteration
                cards = sorted(cards, reverse=True)
                total_card_index += 1

                #See if run is valid
                for ii in range(len(cards)-1):
                    if(cards[ii]-1 != cards[ii+1]):
                        complete_run = False
                        break

                #If valid run, get number of points and reset complete_run
                if(complete_run == True):
                    points = len(cards)
                complete_run = True

        #Check for pairs
        num_cards_checked = 1
        is_done = False
        while (len(old_cards) >= num_cards_checked) and not is_done:
            if cur_card.value == old_cards[num_cards_checked*-1].value:
                num_cards_checked += 1
            else:
                is_done = True
        
        #If any points, use combination formula (num_cards_checked choose 2) to get point values of pair
        if num_cards_checked >= 2:
            points += floor(factorial(num_cards_checked) / (2 * factorial(num_cards_checked-2))) * 2

        if(sum == 15 or sum == 31): #Check for 15 and 31
            points += 2

        return points
    
    #Returns the player whose crib it is
    def get_crib_player(self):
        return self.players[self.crib_index % len(self.players)]

    #Returns the player whose turn it is to peg
    def get_peg_player(self):
        return self.players[self.pegging_index]
    
    #Returns crib
    def get_crib(self) -> list[deck.Card]:
        return copy.copy(self.crib)