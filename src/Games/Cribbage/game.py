#Foreign imports
import PyQt6.QtWidgets as qtw
import os
import pygame as pg
from pygame.locals import *
from PIL import Image
from math import floor
import copy

#Local imports
import home
import deck as dk
import calculate_points as cp

deck = dk.Deck() #Deck you play with
players = [] #List of Discord users that are playing
points = [] #Number of points, indexed same as players
hands = [] #Hands, indexed same as players
backup_hands = [] #Hands that always have hand_size cards, indexed same as players
thrown_cards = []
crib = [] #Crib cards
end = [] #List of players who wish to prematurely end the game
num_thrown = [] #Number of cards thrown in crib, indexed same as players
pegging_list = [] #List of cards in pegging round
point_goal = 121 #Number of points to win
skunk_length = 30 #Number of points from skunk line to end -1
crib_count = 4 #Number of cards in crib
hand_size = 4 #Number of cards in a hand after throwing to crib
crib_index = 0 #crib_index++ each round. Crib belongs to players[crib_index%len(players)]
pegging_index = 0 #(crib_index + 1) % len(players)
throw_count = 0 #How many cards each player throws, initialized upon starting game
game_started = False #True if the game has begun, else False
throw_away_phase = False #True if players still need to throw cards away
pegging_phase = False #True if players are in the pegging phase
calc_string = "" #Saves most recent hand calculations
team_count = 1 #Variable to hold number of players per team (combine points)

#The size of the sprites
base_card_width = 32 #Excess room on sprite sheet
base_card_height = 32 #Excess room on sprite sheet
card_width = 32
card_height = 48
num_width = 16
num_height = 16
base_num_width = 9 * card_width + base_card_width
base_num_height = 4 * card_height + base_card_height + 8
sprite_scalar = 3

#Creates the GUI
#TODO: Maybe have the GUI do something?
def initUI(window, num_cards):
    #Set widgets to be displayed (central widget necessary)
    centralWidget = qtw.QWidget()
    window.setCentralWidget(centralWidget)
    window.layout = qtw.QVBoxLayout(centralWidget)

    #Add the back to home button
    window.home = qtw.QPushButton("Back to Home")
    window.home.clicked.connect(lambda x: home.initUI(window))
    window.layout.addWidget(window.home)
    window.textBrowser = qtw.QTextBrowser()
    window.textBrowser.setOpenExternalLinks(True)
    window.textBrowser.setStyleSheet('font-size: 30px;')
    window.textBrowser.append('Link to cribbage Discord bot can be found <a href=https://github.com/AbbeyRDuBois/Cribbage_Counter>here</a>!')
    window.layout.addWidget(window.textBrowser)

#Starts the game
def start_game():
    global game_started
    global throw_away_phase
    global pegging_index
    global crib_index
    global players
    global hands
    global deck
    global hand_size
    global throw_count

    if(game_started == False):
        #Change game phase
        game_started = True
        throw_away_phase = True
        pegging_index = (crib_index + 1) % len(players)

        #Initiate game vars
        create_game(len(players))
        
        #Get hands
        hands = deck.get_hands(len(players), hand_size + throw_count)

#Checks if player can peg
def can_peg(hand, cur_sum):
    #Check for basic case before iterating. Probably doesn't save time for small hands, but whatever.
    if(cur_sum <= 21 and len(hand) > 0):
        return True
    else:
        for card in hand:
            if(card.to_int_15s() + cur_sum <= 31):
                return True
    return False

#Returns a player that won or None if no winner
def get_winner():
    global players
    global point_goal
    global team_count
    global points

    point_array = points

    if team_count != 1:
        point_array = get_point_array()

    for player_index in range(len(point_array)):
        if(point_array[player_index] >= point_goal):
            return players[player_index]

    return None
        
#Resets the round by changing variables
def reset_round():
    global deck
    global pegging_phase
    global throw_away_phase
    global pegging_list
    global crib_index
    global pegging_index
    global hands
    global backup_hands
    global crib
    global calc_string
    global players
    global hand_size
    global throw_count
    global thrown_cards

    deck.reset_deck()
    pegging_phase = False
    throw_away_phase = True
    pegging_list = []
    crib_index += 1
    pegging_index = (crib_index + 1) % len(players)
    hands = []
    backup_hands = []
    crib = []
    thrown_cards = [[] for _ in range(len(players))]

    for ii in range(len(num_thrown)):
        num_thrown[ii] = 0

    #Get hands for next round
    hands = deck.get_hands(len(players), hand_size + throw_count)
    backup_hands = []

#Ends the game by resetting every variable to standard cribbage
def end_game():
    global players
    global team_count
    players = []
    team_count = 1
    standard_mode()
   
#Gets the path for the images
def get_path(limited_path):
    # if(EXECUTABLE_MODE):
    #     return sys.executable.rsplit('\\', 1)[0] + '\\' + limited_path
    # else:
    return os.path.join(os.path.dirname(__file__), limited_path)
    
#Get string of hand to print for player at given index
def get_hand_string(player_index):
    global hands

    output_string = f"Hand:\n"
    for card in [card.display() for card in sorted(hands[player_index], key=lambda x: x.to_int_runs())]:
        output_string += f"{card}, "
    output_string = output_string[:-2] + "\n"
    for card in [card for card in sorted(hands[player_index], key=lambda x: x.to_int_runs())]:
        output_string += f"!{hands[player_index].index(card)},\t\t"
    output_string = output_string[:-3] + "\n"

    return output_string

#Get picture of hand using "all_assets" in "card_art"
async def get_hand_pic(plyr_index, card=None, show_index=True):
    global players
    global crib
    global hands

    global base_card_width #Excess room on sprite sheet
    global base_card_height #Excess room on sprite sheet
    global card_width
    global card_height
    global num_width
    global num_height
    global base_num_width
    global base_num_height
    global sprite_scalar

    #If a single card is passed in, ignore index and just display the card.
    #Else, get hand if index is valid, or crib if index is negative.
    player_index = copy.copy(plyr_index)
    if card != None:
        print(card.display)
        hand = [copy.copy(card)]
    else:
        if player_index == -1:
            hand = crib
        else:
            try:
                hand = hands[player_index]
            except:
                print("Invalid player index in get_hand_pic.")
                return ""
        

    asset_file_path = get_path('card_art\\all_assets.png')
    card_file_path = get_path('card_art\\card' + str(player_index) + '.png')
    index_file_path = get_path('card_art\\index' + str(player_index) + '.png')

    output_string = ""

    #Stores index number
    card_index = 0

    #Create empty image with place for images
    hand_image = Image.new('RGB', (card_width*len(hand)*sprite_scalar, card_height*sprite_scalar), color=(0, 80, 80))

    #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
    for card in [card for card in sorted(hand, key=lambda x: x.to_int_runs())]:
        if card.value != dk.JOKER:
            #Get right column
            width_multiplier = 4 * floor((card.to_int_runs()-1) / 3)

            #Get right sub-column based on suit
            if card.suit == dk.DIAMOND:
                width_multiplier += 1
            if card.suit == dk.CLUB:
                width_multiplier += 2
            if card.suit == dk.HEART:
                width_multiplier += 3

            #Get right row
            height_multiplier = (card.to_int_runs()+2) % 3

        else:
            height_multiplier = 1
            width_multiplier = 16 #Fourth column * 4 cards in each column

            if card.suit == dk.RED:
                width_multiplier += 1

        x_coord = card_width * width_multiplier + base_card_width
        y_coord = card_height * height_multiplier + base_card_height

        sheet = pg.image.load(asset_file_path)
        card_image = sheet.subsurface((x_coord, y_coord, card_width, card_height))

        pg.image.save(pg.transform.rotozoom(card_image, 0, sprite_scalar), card_file_path)

        card_img = Image.open(card_file_path)

        #Add index (![0-9]) to card
        if show_index == True:
            index_img = Image.new('RGB', (floor(card_width*sprite_scalar/2), floor(card_height*sprite_scalar/2)), color=(0, 0, 0))

            index = hand.index(card)

            if index != 0:
                num_width_multiplier = (index+2) % 3
                num_height_multiplier = floor((index-1) / 3)
            else:
                num_width_multiplier = 1
                num_height_multiplier = 3

            x_num_coord = num_width * num_width_multiplier + base_num_width
            y_num_coord = num_height * num_height_multiplier + base_num_height

            num_image = sheet.subsurface((x_num_coord, y_num_coord, num_width, num_height))

            pg.image.save(pg.transform.rotozoom(num_image, 0, sprite_scalar), index_file_path)

            index_img.paste(Image.open(index_file_path), (floor(card_width*sprite_scalar*3/16), floor(card_height*sprite_scalar*3/16)))
            card_img.paste(index_img, (floor(card_width*sprite_scalar/4), floor(card_height*sprite_scalar/4)))

            #Add index to output string
            output_string += "!" + str(index) + '\t  '

            #Delete created image
            os.remove(index_file_path)

        #Add card to line
        hand_image.paste(card_img, (card_index*card_width*sprite_scalar, 0))

        #Increment to next index
        card_index += 1

    #Ensure concurrency for when throwing away multiple cards in rapid succession
    try:
        if not os.path.exists(get_path('card_art\\hand' + str(player_index) + '.png')):
            hand_file_path = get_path('card_art\\hand' + str(player_index) + '.png')
        else:
            hand_file_path = get_path('card_art\\hand' + str(player_index + len(players)) + '.png')
    except:
        hand_file_path = get_path('card_art\\hand' + str(player_index + len(players)) + '.png')

    #Save hand image
    hand_image.save(hand_file_path)

    #Delete created image
    os.remove(card_file_path)

    #Return image path
    return hand_file_path

#Get single picture with all hands in it
async def get_all_hand_pics():
    global players
    global hands

    global base_card_width #Excess room on sprite sheet
    global base_card_height #Excess room on sprite sheet
    global card_width
    global card_height
    global num_width
    global num_height
    global base_num_width
    global base_num_height
    global sprite_scalar

    all_hands_file_path = get_path('card_art\\all_hands.png')

    #Stores index number
    hand_index = 0
    max_hand_len = 4

    for hand in hands:
        if len(hand) > max_hand_len:
            max_hand_len = len(hand)

    #Create empty image with place for images
    all_hands_img = Image.new('RGB', (card_width*max_hand_len*sprite_scalar, card_height*sprite_scalar*len(hands)), color=(0, 80, 80))

    #Create list of hand pics to delete
    hand_paths = []

    #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
    for hand_index in range(len(hands)):
        #Extra variable because load doesn't like indexing into an array for some reason
        hand_paths.append(await get_hand_pic(hand_index))
        hand_img = Image.open(hand_paths[-1])

        all_hands_img.paste(hand_img, (0, card_height*sprite_scalar*hand_index))

    #Save massive hand pic
    all_hands_img.save(all_hands_file_path)

    #Delete created image
    for path in hand_paths:
        os.remove(path)

    #Return image path
    return all_hands_file_path


#Sets up game to work with num_players amount of people
def create_game(num_players):
    global throw_count
    global points
    global end
    global num_thrown
    global crib_count
    global point_goal
    global skunk_length
    global thrown_cards

    if(num_players == 1):
        throw_count = 2
    elif(num_players == 2):
        throw_count = 2
    elif(num_players >= 3):
        throw_count = 1
    elif(num_players == 4):
        throw_count = 1
    elif(num_players >= 5 and num_players <= 8):
        throw_count = 1
        crib_count = 8
        point_goal = 241
        skunk_length = 60
    else:
        return
    
    #Initiate player variables
    for _ in range(num_players):
        points.append(0)
        end.append(False)
        num_thrown.append(0)
        thrown_cards.append([])

#Create teams with count number of players if able. Returns True on success and False on error.
def create_teams(count):
    global players
    global team_count

    num_players = len(players)

    #Check for valid number
    if (count < 1):
        return False

    #If teams are even, set variable and return True
    if (num_players % count == 0):
        team_count = count

        return True
    
    #If teams uneven, return False
    return False

#Creates a string to represent each team.
def get_teams_string():
    global players
    global team_count

    num_players = len(players)

    #Get the list of teams
    team_list = ""
    num_teams = num_players // team_count
    for team_num in range(num_teams):
        team_list += f"Team {team_num}: "
        for player in range(team_count):
            team_list += f"{players[player*num_teams + team_num]}, "
        team_list = team_list[:-2] + "\n"

    return team_list

#Change a joker in the hand of the specified player. Returns True on success and False if no joker.
def change_hand_joker(card, player):
    global players
    global hands

    #Type check variable before we set
    if not isinstance(card, dk.Card):
        return False

    try:
        player_index = players.index(player)
    except:
        return False

    #Change joker in hand to specified card
    for card_index in range(len(hands[player_index])):
        if hands[player_index][card_index].value == dk.JOKER:
            hands[player_index][card_index] = card

            return True
    
    #If joker not found, return False
    return False

#Changes joker that was flipped up. Returns True on success and False if no joker or if incorrect player.
def change_flipped_joker(card, player):
    global crib_index
    global players
    global deck
    global throw_away_phase
    global pegging_phase

    #Type check variable before we set
    if not isinstance(card, dk.Card):
        return False

    try:
        player_index = players.index(player)
    except:
        return False

    #If player flipped the card, if it's a joker, change flipped to specified card and initialize variables for next round
    if (crib_index % len(players)) == player_index:
        if deck.get_flipped().value == dk.JOKER:
            deck.flipped = card
            throw_away_phase = False
            pegging_phase = True

            #Calculate nibs and add points accordingly
            num_points = cp.nibs(card)
            points[crib_index % len(players)] += num_points

            return True
            
    #If wrong player or flipped card isn't joker, return False
    return False

#Change joker in crib. Returns True on success and False if no joker or if incorrect player.
def change_crib_joker(card, player):
    global crib_index
    global crib

    #Type check variable before we set
    if not isinstance(card, dk.Card):
        return False
    
    try:
        player_index = players.index(player)
    except:
        return False
    
    #If player's crib and if crib has a joker, change to specified card
    if (crib_index % len(players)) == player_index:
        #Change joker in crib to specified card
        for card_index in range(len(crib)):
            if crib[card_index].value == dk.JOKER:
                crib[card_index] = card

                return True
    
    #If not player's crib or if crib doesn't have a joker, return False
    return False

#Checks if there is at least one joker in someone's hand. Returns first player with a joker if there is. Else, returns None.
def check_hand_joker():
    global hands
    global players
    
    #If someone has a joker card (joker mode), return the player with a joker.
    for hand_index in range(len(hands)):
        for card in hands[hand_index]:
            if card.value == dk.JOKER:
                return players[hand_index]
            
    #If no joker was found in hands, return None
    return None

#Checks if there is a joker in the crib. Returns True if there is. Else, returns False.
def check_crib_joker():
    global crib

    for card in crib:
        if card.value == dk.JOKER:
            return True
    
    return False

#Throws away the specified card from the specified player. Returns True on success and False on failure.
def throw_away_card(player, card_index):
    global players
    global hands
    global num_thrown
    global throw_count
    global crib

    #Get player index
    try:
        player_index = players.index(player)
    except:
        return False

    #Make sure player isn't throwing extra away
    if(num_thrown[player_index] < throw_count):
        #Add card to crib and remove from hand
        card = hands[player_index][card_index]
        crib.append(card)
        hands[player_index].remove(card)
        num_thrown[player_index] += 1
        thrown_cards[player_index].append(card)

        return True

    #If player has already thrown away enough cards, return False
    return False

#Checks if player has thrown away enough cards. Returns True if all cards have been thrown. Else, returns False.
def is_finished_throwing(player):
    global num_thrown
    global throw_count

    #Get player index
    try:
        player_index = players.index(player)
    except:
        return False

    #If player hasn't thrown enough cards away, return False.
    if(num_thrown[player_index] < throw_count):
        return False

    #If player has thrown enough cards away, return True.
    return True
    
#Checks if everyone has thrown away enough cards. Returns True if all cards have been thrown. Else, returns False.
def everyone_is_finished_throwing():
    global num_thrown
    global throw_count

    #If any player hasn't thrown enough cards away, return False.
    for player_index in range(len(num_thrown)):
        if(num_thrown[player_index] < throw_count):
            return False

    #If every player has thrown enough cards away, return True.
    return True

#Prepare variables for pegging round
def prepare_pegging():
    global backup_hands
    global hands
    global deck
    global crib_index
    global points
    global players
    global crib
    global crib_count
    global throw_away_phase
    global pegging_phase

    backup_hands = copy.deepcopy(hands)
    flipped = deck.get_flipped()

    #Calculate nibs and add points accordingly
    num_points = cp.nibs(flipped)
    points[crib_index % len(players)] += num_points

    #Make sure crib has proper number of cards
    while(len(crib) < crib_count):
        crib.append(deck.get_card())
    
    #Make sure variables are set up for pegging round
    if flipped.value != dk.JOKER:
        throw_away_phase = False
        pegging_phase = True

#Resets variables for end of pegging round. Return sum of pegging_list.
def pegging_done():
    global calc_string
    global pegging_phase
    global pegging_list
    global pegging_index
    global hands
    global backup_hands

    #Prepare for next round
    pegging_phase = False
    my_sum = sum([my_card.to_int_15s() for my_card in pegging_list])
    pegging_index += 1
    pegging_list = []

    #Restore the siphoned hands to their former glory
    hands = backup_hands

    #Reset calc_string so that it can be filled with new data
    calc_string = ""

    return my_sum

#Calculate hands, add points, and return a string with the details.
def count_hand(player):
    global deck
    global calc_string
    global players
    global hands
    global crib_index

    #Get player index
    try:
        player_index = players.index(player)
    except:
        return ""

    #Variable to hold output
    output_string = ""

    #Add points from hand
    [get_points, get_output] = cp.calculate_hand(hands[(player_index + crib_index + 1) % len(players)], deck.get_flipped())
    points[(player_index + crib_index + 1) % len(players)] += get_points

    #Send calculation to variable in game.py
    calc_string += f"**{players[(player_index + crib_index + 1) % len(players)]}'s Hand**:\n" + get_output + "\n\n"

    #Add data to group output
    output_string += f"{players[(player_index + crib_index + 1) % len(players)].name}'s hand: {[hand_card.display() for hand_card in sorted(hands[(player_index + crib_index + 1) % len(players)], key=lambda x: x.to_int_runs())]} for {get_points} points.\n"

    return output_string

def count_crib():
    global deck
    global calc_string
    global players
    global crib
    global crib_index
    
    #Calculate crib
    [get_points, get_output] = cp.calculate_crib(crib, deck.flipped)
    points[crib_index % len(players)] += get_points
    output_string = f"{players[crib_index % len(players)].name}'s crib: {[crib_card.display() for crib_card in sorted(crib, key=lambda x: x.to_int_runs())]} for {get_points} points."
    
    #Send calculation to variable in game.py
    calc_string += f"**{players[crib_index % len(players)]}'s Crib**:\n" + get_output + "\n\n"

    #Add total points for each person to the group chat variable
    output_string += f"\nTotal Points:\n{get_point_string()}"

    return output_string

#The given player pegs the given card and gets associated points. Returns [number of points, old pegging sum, current pegging sum, cards remaining, card played, next player] on success and None on failure.
def peg(player, card_index):
    global players
    global hands
    global pegging_list
    global points
    global pegging_index

    #Get player index
    try:
        main_player_index = players.index(player)
        card = hands[main_player_index][card_index]
    except:
        return None

    #Make sure it's author's turn
    if(players[pegging_index % len(players)] != players[main_player_index]):
        return None

    cur_sum = sum([my_card.to_int_15s() for my_card in pegging_list]) + card.to_int_15s()

    #Make sure sum <= 31
    if(cur_sum <= 31):
        #Remove card from hand, get points, and add to pegging list
        hands[main_player_index].remove(card)
        peg_points = cp.check_points(card, pegging_list, cur_sum)
        points[main_player_index] += peg_points
        pegging_list.append(card)

        #Make sure that someone has a hand
        for player_index in range(len(players)):
            if(len(hands[player_index]) > 0):
                new_sum = sum([my_card.to_int_15s() for my_card in pegging_list])
                
                #Make sure next person can play. If go, then reset.
                for _ in range(len(players)):
                    pegging_index += 1

                    if(can_peg(hands[pegging_index % len(players)], new_sum)):
                        return [peg_points, cur_sum, new_sum, len(hands[main_player_index]), card, players[pegging_index % len(players)]]
                
        #If nobody can peg, reset variables for next pegging iteration (up to 31)
        pegging_list = []
        if(cur_sum != 31):
            points[pegging_index % len(players)] += 1
            peg_points += 1
        pegging_index += 1

        #Make sure next person has a hand. If not, then increment.
        for _ in range(len(players)):
            if(len(hands[pegging_index % len(players)]) > 0):
                #If here, return points, a new_sum of 0, and player
                return [peg_points, cur_sum, 0, len(hands[main_player_index]), card, players[pegging_index % len(players)]]
            else:
                pegging_index += 1

        #Return variables and none since no player has a hand
        return [peg_points, cur_sum, 0, len(hands[main_player_index]), card, None]
    
    #If player can't play that card, return None
    return None

#Ends the game and returns a string with point details.
def get_winner_string(winner, show_hands=True):
    global players
    global point_goal
    global skunk_length
    global hands
    global backup_hands
    global crib
    global crib_index
    global deck

    player_scores = ""
    player_hands = ""
    winner_string = winner.name

    #Shows the hands
    if(show_hands):
        #Make sure that backup_hands has been initialized
        if(len(backup_hands) == len(players)):
            player_hands += f"Flipped card is: {deck.get_flipped().display()}\n"
            for hand_index in range(len(players)):
                player_hands += f"{players[hand_index]}'s hand: {[card.display() for card in sorted(backup_hands[hand_index], key=lambda card:card.to_int_15s())]}\n"

        #Make sure that crib has been initialized
        if(len(crib) == crib_count):
            player_hands += f"{players[crib_index%len(players)]}'s crib: {[card.display() for card in sorted(crib, key=lambda card:card.to_int_15s())]}\n"

    #Shows the ending point totals
    point_array = get_point_array()
    for point_index in range(len(point_array)):
        if(point_array[point_index] < (point_goal - skunk_length)):
            if team_count == 1: #If no teams, display based on name
                player_scores += f"{players[point_index]} got skunked x{(point_goal - point_array[point_index]) // skunk_length} at {point_array[point_index]} points.\n"
            else: #If teams, display by team
                num_teams = len(players) // team_count
                player_scores += f"Team {point_index} ("
                for player in range(num_teams):
                    player_scores += f"{players[player*num_teams + point_index]}, "
                player_scores = player_scores[:-2] + f") got skunked x{(point_goal - point_array[point_index]) // skunk_length} at {point_array[point_index]} points.\n"
        else:
            if team_count == 1: #If no teams, display based on name
                player_scores += f"{players[point_index]} ended with {point_array[point_index]} points.\n"
            else: #If teams, display by team
                num_teams = len(players) // team_count
                team = f"Team {point_index} ("
                for player in range(team_count):
                    team += f"{players[player*num_teams + point_index]}, "
                team = team[:-2] + ")"

                #If this team won, replace winner_string with team
                if(point_array[point_index] >= point_goal):
                    winner_string = team

                #Add team and point data to output string player_scores
                player_scores += team + f" ended with {point_array[point_index]} points.\n"

    end_game()
    return player_hands + player_scores + f"{winner_string} has won the game! Everything will now be reset."

#Returns a string with each team and the number of points they have
def get_point_string(always_solo=False):
    global team_count
    global players
    global points

    output_string = ""

    #If playing alone, don't have team names
    #Else, print out teams and points for team
    if team_count == 1 or always_solo == True:
        for player_index in range(len(players)):
            output_string += f"{players[player_index].name} has {points[player_index]} points.\n"
    else:
        point_count = 0
        num_teams = len(players) // team_count

        for team_num in range(num_teams):
            output_string += f"Team {team_num} ("
            for player in range(team_count):
                point_count += points[player*num_teams + team_num]
                output_string += f"{players[player*num_teams + team_num]}, "
            output_string = output_string[:-2] + f") has {point_count} points.\n"
            point_count = 0

    return output_string[:-1]

def get_point_array():
    global team_count
    global players
    global points

    output_string = ""
    point_array = []

    point_count = 0
    num_teams = len(players) // team_count

    for team_num in range(num_teams):
        for player in range(team_count):
            point_count += points[player*num_teams + team_num]
        point_array.append(point_count)
        point_count = 0

    return point_array

#Sets up game for standard mode
def standard_mode():
    global deck
    global points
    global hands
    global backup_hands
    global crib
    global end
    global num_thrown
    global pegging_list
    global point_goal
    global skunk_length
    global crib_count
    global hand_size
    global crib_index
    global pegging_index
    global throw_count
    global game_started
    global throw_away_phase
    global pegging_phase

    deck = dk.Deck()
    points = []
    hands = []
    backup_hands = []
    crib = []
    end = []
    num_thrown = []
    pegging_list = []
    point_goal = 121
    skunk_length = 30
    crib_count = 4
    hand_size = 4
    crib_index = 0
    pegging_index = 0
    throw_count = 0
    game_started = False
    throw_away_phase = False
    pegging_phase = False

#Sets up game for mega hand
def mega_hand():
    global game_started
    global point_goal
    global skunk_length
    global hand_size

    if(game_started == False):
        point_goal = 241
        skunk_length = 60
        hand_size = 8

#Sets up game for joker mode
def joker_mode():
    global game_started
    global deck

    if(game_started == False):
        deck = dk.JokerDeck()