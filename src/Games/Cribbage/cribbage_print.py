import copy
import itertools
from collections import OrderedDict
import discord

from Games.Cribbage.cribbage import Cribbage
from Games.game_print import game_print
import Games.deck as dk

class Cribbage_Print(game_print):
    def __init__(self):
        super().__init__()
        self.game = Cribbage()
        self.commands["^![0-9]+$"] = [self.select_card, self.select_card_parse]
        self.commands["^![a2-9jqk]|10 [hdcs]$"] = [self.make_joker]
        self.commands["^!standard$"] = [self.play_standard]
        self.commands["^!mega$"] = [self.play_mega]
        self.commands["^!joker$"] = [self.play_joker]

        hand_messages = [] #Variable to hold most recent hand message so that it can be modified as needed

        self.calc_string = "" #Saves most recent hand calculations

    #Input: player and str as defined in message.py for commands
    #Output: add_return print for message handler
    def play_standard(self, player, _sent_str):
        if player in self.game.players:
            self.game.standard_mode()
        else:
            return self.add_return([], player.name + f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        
    #Input: player and str as defined in message.py for commands
    #Output: add_return print for message handler
    def play_mega(self, player, _sent_str):
        if player in self.game.players:
            self.game.mega_hand()
        else:
            return self.add_return([], player.name + f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        
    #Input: player and str as defined in message.py for commands
    #Output: add_return print for message handler
    def play_joker(self, player, _sent_str):
        if player in self.game.players:
            self.game.joker_mode()
        else:
            return self.add_return([], player.name + f"You can't start a game you aren't queued for, {player.name}. Use !join to join the game.")
        
    #Input: player and team_count as defined in default_print
    #Output: add_return print for message handler
    #NOTE: predefined function from base class
    def create_teams(self, _player, team_count:int):
        #If teams are even, start game
        if (self.game.create_teams(team_count) == True):
            #Add the teams to be printed before the start returns (index=0)
            return self.add_return([], f"Teams of {team_count} have been formed:\n{self.game.get_teams_string()}", index=0)
        else:
            return False, self.add_return([], "There must be an equal number of players on each team in order to form teams.")

    #Input: parse string of form "^![0-9]+$"
    #Output: integer index parsed from string in list
    def select_card_parse(self, parse_str):
        return [int(parse_str[1:])]

    #Input: integer index parsed from string
    #Output: list of return statements using add_return
    def select_card(self, player, index):
        if(player in self.game.players):
            #Check for valid index or return
            if(index >= len(self.game.hands[self.game.players.index(player)]) or index < 0):
                return []

            if(self.game.game_started == True):
                if(self.game.throw_away_phase == True):
                    return self.throw_away_phase_func(player, index)
                elif(self.game.pegging_phase == True):
                    return self.pegging_phase_func(player, index)

        return []

    async def throw_away_phase_func(self, author, card_index):
        return_list = []

        #Don't do anything if player not in game.
        if(author not in self.game.players):
            return return_list
        
        #If player has joker card (joker mode), force them to make joker something before anybody throws.
        if self.game.check_hand_joker() != None:
            return self.add_return(return_list, f"You can't throw away cards until {self.game.check_hand_joker().name} has chosen which card to turn their joker into.")

        #If throwing away a card fails, alert player.
        if(self.game.throw_away_card(author, card_index) == False):
            return self.add_return(return_list, f"You have already thrown away the required number of cards, {author.name}.")

        #Update hand if applicable.
        await self.update_hand(author)

        #Check if everyone is done. If not, return. Else, get flipped card and begin pegging round.
        if(self.game.is_finished_throwing(author)):
            if(not self.game.everyone_is_finished_throwing()):
                self.add_return(return_list, f'''{author.name} has finished putting cards in the crib.''')
                return return_list
            else:
                self.game.prepare_pegging()
                self.calc_string = "" #Reset calc_string so that it can be filled with new data

                #Add display text
                flipped = self.game.deck.get_flipped()
                if(flipped.value != dk.JACK):
                    self.add_return(return_list, f'''{author.name} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.''')
                else:
                    self.add_return(return_list, f'''{author.name} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.\n{self.game.players[self.game.crib_index % len(self.game.players)]} gets nibs for 2.''')
                
                #Check for winner
                if(self.game.get_winner() != None):
                    return self.add_return(return_list, self.game.get_winner_string(self.game.get_winner()))
                
                #Check for flipped joker
                if(flipped.value == dk.JOKER):
                    self.add_return(return_list, f"***{self.game.players[self.game.crib_index % len(self.game.players)].name} must choose which card to turn the flipped joker into before game can proceed.***")
                else:
                    self.add_return(return_list, f"Pegging will now begin with **{self.game.players[self.game.pegging_index]}**.")
            
        return return_list
    
    async def pegging_phase_func(self, author, card_index):
        return_list = []

        peg_vars = self.game.peg(author, card_index)
        if(peg_vars == None):
            #If pegged out, end game
            if(self.game.get_winner() != None):
                return self.add_return(return_list, self.game.get_winner_string(self.game.get_winner()))
            return return_list

        points = peg_vars[0]
        card = peg_vars[4]
        next_player = peg_vars[5]

        #If a player who can play was found, let them play. Otherwise, increment to next player and reset.
        if(next_player != None):
            #Parse variables
            last_sum = peg_vars[1]
            cur_sum = peg_vars[2]
            cur_player_hand_size = peg_vars[3]

            #Display data
            if(last_sum == cur_sum): #If no reset
                if(points > 0):
                    self.add_return(return_list, f'''{author.name} played {card.display()}, gaining {points} points and bringing the total to {cur_sum}.\nIt is now **{next_player}**'s turn to play.''')
                else:
                    self.add_return(return_list, f'''{author.name} played {card.display()}, bringing the total to {cur_sum}.\nIt is now **{next_player}**'s turn to play.''')
            else:
                if(last_sum == 31):
                    self.add_return(return_list, f'''{author.name} played {card.display()}, got {points} points and reached 31. Total is reset to 0.\nIt is now **{next_player}**'s turn to play.''')
                else:
                    self.add_return(return_list, f'''{author.name} played {card.display()}, got {points} point(s) including last card. Total is reset to 0.\nIt is now **{next_player}**'s turn to play.''')

            #If player is out of cards, add message to print. Else, update hand.
            if(cur_player_hand_size != 0):
                await self.update_hand(author)
            else:
                self.add_return(return_list, f"{author.name} has played their last card.", index=0)
        else:
            #Prepare for next round
            my_sum = self.game.pegging_done()

            #Add last card data to 
            if(my_sum != 31):
                self.add_return(return_list, f'''{author.name} played {card.display()}, got {points} point(s) including last card. Total is reset to 0.\n''')
            else:
                self.add_return(return_list, f'''{author.name} played {card.display()}, got {points} points and reached 31. Total is reset to 0.\n''')
                
            self.add_return(return_list, f"Everyone is done pegging.\n")
            
            if(self.game.check_crib_joker() == False):
                await self.finished_pegging(return_list)
            else:
                self.add_return(return_list, f"***{self.game.players[self.game.crib_index % len(self.game.players)].name} must choose which card to turn the joker in their crib into before game can proceed.***")
                hand_pic = await self.game.get_hand_pic(-1)
                self.add_return(return_list, hand_pic, isFile=True)

        #If pegged out, end game
        if(self.game.get_winner() != None):
            return self.add_return(return_list, self.game.get_winner_string(self.game.get_winner()))

        return return_list
    
    async def finished_pegging(self, return_list):
        self.game.pegging_done()

        output_string = f"Flipped card: {self.game.deck.get_flipped().display()}\n"

        #Calculate points
        for player_index in range(len(self.game.players)):
            output_string += self.game.count_hand(self.game.players[player_index])
            
            #Check for winner
            if(self.game.get_winner() != None):
                return self.add_return(return_list, self.game.get_winner_string(self.game.get_winner()))

        #Calculate crib
        output_string += self.game.count_crib()

        #Check for winner
        if(self.game.get_winner() != None):
            return self.add_return(return_list, self.game.get_winner_string(self.game.get_winner()))

        #Reset variables for the next round
        self.game.reset_round()

        #Update hand if applicable
        for player_index in range(len(self.game.players)):
            await self.update_hand(self.game.players[player_index])

        #Finalize and send output_string to group chat
        output_string += f'''\nThrow {self.game.throw_count} cards into **{self.game.players[self.game.crib_index % len(self.game.players)]}**'s crib.\n*Use "/h" or "/hand" to see your hand.*'''

        return self.add_return(return_list, output_string)

    #Function to turn joker into another card
    async def make_joker(self, author, message):
        return_list = []

        if author in self.game.players:
            value = ''
            suit = ''

            #Split message into number and suit letter
            try:
                value_list = message[1:].split()

                #Get value of card
                match value_list[0]:
                    case 'a':
                        value = dk.ACE
                    case 'j':
                        value = dk.JACK
                    case 'q':
                        value = dk.QUEEN
                    case 'k':
                        value = dk.KING
                    case _:
                        value = value_list[0]

                #Get suit of card
                match value_list[1]:
                    case 'h':
                        suit = dk.HEART
                    case 'd':
                        suit = dk.DIAMOND
                    case 'c':
                        suit = dk.CLUB
                    case 's':
                        suit = dk.SPADE
            except:
                return self.add_return(return_list, "Failed to parse joker message.")
            
            #Create card and get player index
            card = dk.Card(value, suit)

            if self.game.change_hand_joker(card, author) == True:
                #Update hand if applicable
                await self.update_hand(author)

                return self.add_return(return_list, f"Joker in hand has been made into {card.display()}.")
                
            #Change flipped joker to specified card
            elif self.game.change_flipped_joker(card, author) == True:
                if(card.value == dk.JACK):
                    self.add_return(return_list, f"Flipped joker has been made into {card.display()}.\n{self.game.players[self.game.crib_index % len(self.game.players)]} gets nibs for 2.\nPegging will now begin with **{self.game.players[self.game.pegging_index]}**")
                    
                    #Check for winner
                    if(self.game.get_winner() != None):
                        return self.add_return(return_list, self.game.get_winner_string(self.game.get_winner()))
                
                    return return_list
                else:
                    return self.add_return(return_list, f"Flipped joker has been made into {card.display()}.\nPegging will now begin with **{self.game.players[self.game.pegging_index]}**")
                
            #Change joker in crib to specified card
            elif self.game.change_crib_joker(card, author) == True:
                self.add_return(return_list, f"Joker in crib has been made into {card.display()}.")
                await self.finished_pegging(return_list)
                return return_list

            return self.add_return(return_list, f"You need to have a joker in order to use this command, {author.name}.")
        
        return self.add_return(return_list, f"You need to be in the game to play, {author.name}. Use !join between games to join.")
    
    #Calculate hands, add points, and return a string with the details.
    def count_hand(self, player):
        #Get player index
        try:
            player_index = self.game.players.index(player)
        except:
            return ""

        #Variable to hold output
        output_string = ""

        #Add points from hand
        [get_points, get_output] = self.calculate_hand(self.game.hands[(player_index + self.game.crib_index + 1) % len(self.game.players)], self.game.deck.get_flipped())
        self.game.points[(player_index + self.game.crib_index + 1) % len(self.game.players)] += get_points

        #Send calculation to variable in game.py
        self.calc_string += f"**{self.game.players[(player_index + self.game.crib_index + 1) % len(self.game.players)]}'s Hand**:\n" + get_output + "\n\n"

        #Add data to group output
        output_string += f"{self.game.players[(player_index + self.game.crib_index + 1) % len(self.game.players)].name}'s hand: {[hand_card.display() for hand_card in sorted(self.game.hands[(player_index + self.game.crib_index + 1) % len(self.game.players)], key=lambda x: x.to_int_runs())]} for {get_points} points.\n"

        return output_string

    def count_crib(self):
        #Calculate crib
        [get_points, get_output] = self.game.calculate_crib(self.game.crib, self.game.deck.flipped)
        self.game.points[self.game.crib_index % len(self.game.players)] += get_points
        output_string = f"{self.game.players[self.game.crib_index % len(self.game.players)].name}'s crib: {[crib_card.display() for crib_card in sorted(self.game.crib, key=lambda x: x.to_int_runs())]} for {get_points} points."
        
        #Send calculation to variable in game.py
        self.calc_string += f"**{self.game.players[self.game.crib_index % len(self.game.players)]}'s Crib**:\n" + get_output + "\n\n"

        #Add total points for each person to the group chat variable
        output_string += f"\nTotal Points:\n{self.get_point_string()}"

        return output_string

    #Get string of hand to print for player at given index
    def get_hand_string(self, player_index):
        output_string = f"Hand:\n"
        for card in [card.display() for card in sorted(self.game.hands[player_index], key=lambda x: x.to_int_runs())]:
            output_string += f"{card}, "
        output_string = output_string[:-2] + "\n"
        for card in [card for card in sorted(self.game.hands[player_index], key=lambda x: x.to_int_runs())]:
            output_string += f"!{self.game.hands[player_index].index(card)},\t\t"
        output_string = output_string[:-3] + "\n"

        return output_string

    #Creates a string to represent each team.
    def get_teams_string(self):
        num_players = len(self.game.players)

        #Get the list of teams
        team_list = ""
        num_teams = num_players // self.game.team_count
        for team_num in range(num_teams):
            team_list += f"Team {team_num}: "
            for player in range(self.game.team_count):
                team_list += f"{self.game.players[player*num_teams + team_num]}, "
            team_list = team_list[:-2] + "\n"

        return team_list

    #Ends the game and returns a string with point details.
    def get_winner_string(self, winner, show_hands=True):
        player_scores = ""
        player_hands = ""
        winner_string = winner.name

        #Shows the hands
        if(show_hands):
            #Make sure that backup_hands has been initialized
            if(len(self.game.backup_hands) == len(self.game.players)):
                player_hands += f"Flipped card is: {self.game.deck.get_flipped().display()}\n"
                for hand_index in range(len(self.game.players)):
                    player_hands += f"{self.game.players[hand_index]}'s hand: {[card.display() for card in sorted(self.game.backup_hands[hand_index], key=lambda card:card.to_int_15s())]}\n"

            #Make sure that crib has been initialized
            if(len(self.game.crib) == self.game.crib_count):
                player_hands += f"{self.game.players[self.game.crib_index%len(self.game.players)]}'s crib: {[card.display() for card in sorted(self.game.crib, key=lambda card:card.to_int_15s())]}\n"

        #Shows the ending point totals
        point_array = self.game.get_point_array()
        for point_index in range(len(point_array)):
            if(point_array[point_index] < (self.game.point_goal - self.game.skunk_length)):
                if self.game.team_count == 1: #If no teams, display based on name
                    player_scores += f"{self.game.players[point_index]} got skunked x{(self.game.point_goal - point_array[point_index]) // self.game.skunk_length} at {point_array[point_index]} points.\n"
                else: #If teams, display by team
                    num_teams = len(self.game.players) // self.game.team_count
                    player_scores += f"Team {point_index} ("
                    for player in range(num_teams):
                        player_scores += f"{self.game.players[player*num_teams + point_index]}, "
                    player_scores = player_scores[:-2] + f") got skunked x{(self.game.point_goal - point_array[point_index]) // self.game.skunk_length} at {point_array[point_index]} points.\n"
            else:
                if self.game.team_count == 1: #If no teams, display based on name
                    player_scores += f"{self.game.players[point_index]} ended with {point_array[point_index]} points.\n"
                else: #If teams, display by team
                    num_teams = len(self.game.players) // self.game.team_count
                    team = f"Team {point_index} ("
                    for player in range(self.game.team_count):
                        team += f"{self.game.players[player*num_teams + point_index]}, "
                    team = team[:-2] + ")"

                    #If this team won, replace winner_string with team
                    if(point_array[point_index] >= self.game.point_goal):
                        winner_string = team

                    #Add team and point data to output string player_scores
                    player_scores += team + f" ended with {point_array[point_index]} points.\n"

        self.game.end_game()
        return player_hands + player_scores + f"{winner_string} has won the game! Everything will now be reset."

    #Returns a string with each team and the number of points they have
    def get_point_string(self, always_solo=False):
        output_string = ""

        #If playing alone, don't have team names
        #Else, print out teams and points for team
        if self.game.team_count == 1 or always_solo == True:
            for player_index in range(len(self.game.players)):
                output_string += f"{self.game.players[player_index].name} has {self.game.points[player_index]} points.\n"
        else:
            point_count = 0
            num_teams = len(self.game.players) // self.game.team_count

            for team_num in range(num_teams):
                output_string += f"Team {team_num} ("
                for player in range(self.game.team_count):
                    point_count += self.game.points[player*num_teams + team_num]
                    output_string += f"{self.game.players[player*num_teams + team_num]}, "
                output_string = output_string[:-2] + f") has {point_count} points.\n"
                point_count = 0

        return output_string[:-1]

    #Finding Nobs
    def nobs(self, hand, flipped, points=0, output_string=''):
        #For Nobs (suit of jack in hand matches the flipped suit)
        for card in hand:
            if (card.suit == flipped.suit) and (card.value == self.game.deck.JACK):
                output_string += "Nobs for 1\n"
                points += 1
                break

        return [points, output_string]

    #Finding 15s
    def find_15s(self, hand, flipped, points=0, output_string=''):
        hand = copy.copy(hand)
        hand.append(flipped)

        for subset_size in range(1, len(hand) + 1):
            for subset in itertools.combinations(hand, subset_size):
                subset_sum = sum(card.to_int_15s() for card in subset)

                if subset_sum == 15:
                    points += 2
                    subset_expression = " + ".join(f"{card.value}" for card in subset)
                    output_string += f"{subset_expression} = 15 ({points})\n"
                    
        return [points, output_string]

    #Finding Pairs
    def find_pairs(self, hand, flipped, points=0, output_string=''):
        hand = copy.copy(hand)
        hand.append(flipped)

        for card1, card2 in itertools.combinations(hand, 2):
            if card1.value == card2.value:
                points += 2
                output_string += f"Pair {card1.value} / {card2.value} ({points})\n"
                
        return [points, output_string]

    #Finding Runs
    def find_runs(self, hand, flipped, points=0, output_string=''):
        #Initialize list of card values
        hand = copy.copy(hand)
        hand.append(flipped)
        hand.sort(key=lambda card: card.to_int_runs(), reverse=True)
        card_values = [card.to_int_runs() for card in hand]
        
        #Set up variables
        multiplier_count = 0 #Counts duplicates in runs for displaying
        total_multiplier = 1 #Total run multiplier (duplicates)
        multiplier = 1 #Local multiplier (duplicates)
        run_length = 1 #Length of the current run

        #Loop through each card
        for index in range(len(card_values)):
            if(index+1 < len(card_values)): #Ensure that overflow doesn't occur
                if(card_values[index] == card_values[index+1]): #If duplicate, add to multiplier
                    multiplier += 1
                else:
                    if(card_values[index] != card_values[index+1] and multiplier > 1): #If duplicate needs resetting
                        multiplier_count += multiplier-1
                        total_multiplier *= multiplier
                        multiplier = 1
                    if(card_values[index]-1 == card_values[index+1]): #If next card continues run (since duplicates are taken care of)
                        run_length += 1
                    elif(run_length >= 3): #If valid run, add points, display, and reset variables
                        multiplier_count += multiplier-1
                        total_multiplier *= multiplier
                        points += run_length * total_multiplier
                        output_string += f"{total_multiplier} run(s) of {run_length}{list(OrderedDict.fromkeys([card.value for card in sorted([hand[i] for i in range(index+1-run_length-multiplier_count, index+1)], key=lambda card: card.to_int_runs())]))} for {run_length * total_multiplier} ({points})\n"

                        multiplier_count = 0
                        total_multiplier = 1
                        multiplier = 1
                        run_length = 1
                    else: #If invalid run, reset variables
                        multiplier_count = 0
                        total_multiplier = 1
                        multiplier = 1
                        run_length = 1
            else: #If no more cards after this one, wrap up with current variables
                if(run_length >= 3):
                    multiplier_count += multiplier-1
                    total_multiplier *= multiplier
                    points += run_length * total_multiplier
                    output_string += f"{total_multiplier} run(s) of {run_length}{list(OrderedDict.fromkeys([card.value for card in sorted([hand[i] for i in range(index+1-run_length-multiplier_count, index+1)], key=lambda card: card.to_int_runs())]))} for {run_length * total_multiplier} ({points})\n"
                    
                #Reset variables just to be safe
                multiplier_count = 0
                total_multiplier = 1
                multiplier = 1
                run_length = 1

        return [points, output_string]

    #Finding Flush
    def find_flush(self, hand, flipped, points=0, output_string='', isCrib = False):
        first_suit = hand[0].suit
        local_points = 0

        if all(card.suit == flipped.suit for card in hand):
            local_points += len(hand) + 1
        elif(not isCrib):
            if all(card.suit == first_suit for card in hand):
                local_points += len(hand)

        if(local_points != 0):
            points += local_points
            output_string += f"Flush of {first_suit} for {local_points}\n"

        return [points, output_string]

    #Calculate the score for a hand
    def calculate_hand(self, hand, flipped):
        points = 0
        output_string = ""

        #Organize the hand
        hand = sorted(hand, key=lambda x: x.value)
        
        output_string += f"Flipped:\n{flipped.value}\n\nHand:\n"
        for card in reversed(hand):
            output_string += f"{card.value}\n"
        
        output_string += "------------------------\n"

        #Calculate points
        [points, output_string] = self.find_15s(hand, flipped, points, output_string)
        [points, output_string] = self.find_pairs(hand, flipped, points, output_string)
        [points, output_string] = self.find_runs(hand, flipped, points, output_string)
        [points, output_string] = self.find_flush(hand, flipped, points, output_string)
        [points, output_string] = self.nobs(hand, flipped, points, output_string)

        output_string += "------------------------\n"
        output_string += f"Total points: {points}"

        return points, output_string

    #Calculate the score for a crib
    def calculate_crib(self, hand, flipped):
        points = 0
        output_string = ""

        #Organize the hand
        hand = sorted(hand, key=lambda x: x.value)
        
        output_string += f"Flipped:\n{flipped.value}\n\nCrib:\n"
        for card in reversed(hand):
            output_string += f"{card.value}\n"
        
        output_string += "------------------------\n"

        #Calculate points
        [points, output_string] = self.find_15s(hand, flipped, points, output_string)
        [points, output_string] = self.find_pairs(hand, flipped, points, output_string)
        [points, output_string] = self.find_runs(hand, flipped, points, output_string)
        [points, output_string] = self.find_flush(hand, flipped, points, output_string, True)
        [points, output_string] = self.nobs(hand, flipped, points, output_string)

        output_string += "------------------------\n"
        output_string += f"Total points: {points}"

        return points, output_string
    
    #Updates a player's hand if applicable.
    async def update_hand(self, player):
        if self.hand_messages[self.game.players.index(player)] != None:
            hand_pic = await self.deck_print.get_hand_pic(self.game.players.index(player))
            await self.hand_messages[self.game.players.index(player)].edit_original_response(attachments=[discord.File(hand_pic)])