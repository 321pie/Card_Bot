import copy

from Games.Cribbage.cribbage import Cribbage
import Games.deck as dk
from Games.game_print import Game_Print
import Games.stats as stats

class Cribbage_Print(Game_Print):
    HAND_PIC = True

    def __init__(self):
        super().__init__()
        self.game = Cribbage()
        self.commands["^!([a2-9jqk]|10) [hdcs]$"] = [self.make_joker, self.make_joker_parse]
        self.commands["^!standard$"] = [self.play_standard]
        self.commands["^!mega$"] = [self.play_mega]
        self.commands["^!joker$"] = [self.play_joker]
        self.commands["^!reverse$"] = [self.play_reverse]
        self.commands["^!teams [0-9]+$"] = [self.create_teams, self.create_team_parse]
        self.commands["^!goal [0-9]+$"] = [self.change_goal, self.change_goal_parse]
        self.commands["^!skunk [0-9]+$"] = [self.change_skunk, self.change_skunk_parse]
        self.commands["^!points$"] = [self.get_points]
        self.commands["^!tpoints$"] = [self.get_team_points]
        self.commands["^!calcs$"] = [self.get_calcs]

        self.calc_string = "" #Saves most recent hand calculations

        #Stats/Achievements variables
        self.standard:bool = True
        self.custom:bool = False
        self.joker:bool = False
        self.mega:bool = False
        self.reverse:bool = False

    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def get_team_points(self, _player):
        return self.add_return([], self.get_point_string())
    
    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def get_points(self, _player):
        return self.add_return([], self.get_point_string(True))

    #Input: command string as defined in message.py for command helper functions
    #Output: the integer goal number passed by the player
    def change_goal_parse(self, parse_str):
        return [int(parse_str[6:])]

    #Input: player as defined in message.py for commands and integer goal_num from change_goal_parse
    #Output: add_return print for message handler
    async def change_goal(self, player, goal_num):
        if player in self.game.get_players():
            if goal_num != 0:
                self.game.point_goal = goal_num
                self.standard = False
                self.custom = True

                return self.add_return([] if goal_num<1000 else self.add_return([], f"You've messed up, hun. Use **!end** to surrender if you even dare to **!start** in the first place."), f"{player} has changed the goal to {goal_num} points. Use **!start** to begin.")
            else:
                return self.add_return([], f"Don't input 0. I better not catch you doing it again. :eyes:")
        return self.add_return([], f"You can't edit a game you're not in, {player}. Use **!join** to join.")

    #Input: command string as defined in message.py for command helper functions
    #Output: the integer goal number passed by the player
    def change_skunk_parse(self, parse_str):
        return [int(parse_str[7:])]

    #Input: player as defined in message.py for commands and integer goal_num from change_skunk_parse
    #Output: add_return print for message handler
    async def change_skunk(self, player, skunk_num):
        if player in self.game.get_players():
            if skunk_num != 0:
                self.game.skunk_length = skunk_num
                self.standard = False
                self.custom = True

                return self.add_return([], f"{player} has changed the skunk interval to {skunk_num} points. Use **!start** to begin.")
            else:
                return self.add_return([], f"Don't input 0. I better not catch you doing it again. :eyes:")
        return self.add_return([], f"You can't edit a game you're not in, {player}. Use **!join** to join.")

    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def play_standard(self, player):
        if player in self.game.get_players():
            self.game.standard_mode()
            self.standard = True
            self.custom = False
            self.joker = False
            self.mega = False
            self.reverse = False

            return self.add_return([], f"{player} has changed the game to standard mode. Use **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def play_mega(self, player):
        if player in self.game.get_players():
            self.game.mega_hand()
            self.standard = False
            self.mega = True

            return self.add_return([], f"{player} has changed the game to mega hand mode. Use !standard to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def play_joker(self, player):
        if player in self.game.get_players():
            self.game.joker_mode()
            self.joker = True
            
            return self.add_return([], f"{player} has changed the game to joker mode. Use !standard to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def play_reverse(self, player):
        if player in self.game.get_players():
            self.game.reverse_mode()
            self.reverse = True
            
            return self.add_return([], f"{player} has changed the game to reverse mode. Use !standard to swap back or **!start** to begin.")
        else:
            return self.add_return([], f"You can't change a game mode you aren't queued for, {player}. Use **!join** to join the game.")
        
    #Input: player as defined in message.py for commands
    #Output: add_return print for message handler
    async def get_calcs(self, player):
        if self.calc_string == "":
            return self.add_return([], f"You need to finish a round before you can see the hand values, {player}.")
        else:
            return self.add_return([], self.calc_string)
        
    #Input: parse string of form "^!teams [0-9]+$"
    #Output: integer team count parsed from the string
    def create_team_parse(self, parse_str):
        return [int(parse_str[7:])]
    
    #Input: player and team_count as defined in default_print
    #Output: add_return print for message handler
    async def create_teams(self, _player, team_count:int):
        #If teams are even, start game
        if (self.game.create_teams(team_count) == True):
            #Add the teams to be printed before the start returns (index=0)
            self.game.start_game()

            #Initialize local vars
            for _ in self.game.get_players():
                self.end.append(False)
                self.hand_messages.append(None)

            return self.add_return([], f"Teams of {team_count} have been formed:\n{self.get_teams_string()}{self.get_start_string(_player)}", index=0)
        else:
            return False, self.add_return([], "There must be an equal number of players on each team in order to form teams.")

    #Input: integer index parsed from string
    #Output: list of return statements using add_return
    async def select_card(self, player, card_index):
        if(player in self.game.get_players()):
            #Check for valid index or return
            if(card_index >= len(self.game.hands[self.game.get_player_index(player)]) or card_index < 0):
                return []

            if(self.game.game_started == True):
                if(self.game.throw_away_phase == True):
                    return await self.throw_away_phase_func(player, card_index)
                elif(self.game.pegging_phase == True):
                    return await self.pegging_phase_func(player, card_index)

        return []

    async def throw_away_phase_func(self, player, card_index):
        return_list = []

        #Don't do anything if player not in game.
        if(player not in self.game.get_players()):
            return return_list
        
        #If player has joker card (joker mode), force them to make joker something before anybody throws.
        if self.game.check_hand_joker() != None:
            return self.add_return(return_list, f"You can't throw away cards until ***{self.game.check_hand_joker()}*** has chosen which card to turn their joker into.")

        #If throwing away a card fails, alert player.
        if(self.game.card_select(player, card_index) == False):
            return self.add_return(return_list, f"You have already thrown away the required number of cards, {player}.")

        #Update hand if applicable.
        await self.update_hand(player)

        #Check if everyone is done. If not, return. Else, get flipped card and begin pegging round.
        if(self.game.is_finished_throwing(player)):
            if not self.game.everyone_is_finished_throwing():
                self.add_return(return_list, f'''{player} has finished putting cards in the crib.''')
                return return_list
            else:
                self.game.prepare_pegging()
                self.calc_string = "" #Reset calc_string so that it can be filled with new data

                #Add display text
                flipped = self.game.deck.get_flipped()
                if(flipped.value != dk.JACK):
                    self.add_return(return_list, f'''{player} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.''', self.deck_look.get_hand_pic([[flipped]], show_index=False))
                else:
                    self.add_return(return_list, f'''{player} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.\n{self.game.get_crib_player()} gets nibs for 2.''', self.deck_look.get_hand_pic([[flipped]], show_index=False))
                
                #Check for winner
                if(self.game.get_winner() != None):
                    return self.get_winner_string(self.game.get_winner(), return_list=return_list)
                
                #Check for flipped joker
                if(flipped.value == dk.JOKER):
                    self.add_return(return_list, f"***{self.game.get_crib_player()} must choose which card to turn the flipped joker into before game can proceed.***")
                else:
                    self.add_return(return_list, f"Pegging will now begin with **{self.game.get_peg_player()}**.")
            
        return return_list
    
    async def pegging_phase_func(self, player, card_index):
        return_list = []

        peg_vars = self.game.peg(player, card_index)
        
        #If pegged out, end game
        if(self.game.get_winner() != None):
            return self.get_winner_string(self.game.get_winner(), return_list=return_list)
        
        if(peg_vars == None):
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
                    self.add_return(return_list, f'''{player} played {card.display()}, gaining {points} points and bringing the total to {cur_sum}.''', self.deck_look.get_hand_pic([[card]], show_index=False))
                else:
                    self.add_return(return_list, f'''{player} played {card.display()}, bringing the total to {cur_sum}.''', self.deck_look.get_hand_pic([[card]], show_index=False))
            else:
                if(last_sum == 31):
                    self.add_return(return_list, f'''{player} played {card.display()}, got {points} points and reached 31. Total is reset to 0.''', self.deck_look.get_hand_pic([[card]], show_index=False))
                else:
                    self.add_return(return_list, f'''{player} played {card.display()}, got {points} point(s) including last card. Total is reset to 0.''', self.deck_look.get_hand_pic([[card]], show_index=False))
            
            #Add player's turn below card played
            self.add_return(return_list, f"It is now **{next_player}**'s turn to play.")

            #If player is out of cards, add message to print. Else, update hand.
            if(cur_player_hand_size != 0):
                await self.update_hand(player)
            else:
                self.add_return(return_list, f"{player} has played their last card.", index=0)
        else:
            #Prepare for next round
            my_sum = self.game.pegging_done()

            #Add last card data to output string
            if(my_sum != 31):
                self.add_return(return_list, f'''{player} played {card.display()}, got {points} point(s) including last card. Total is reset to 0.\n''', self.deck_look.get_hand_pic([[card]], show_index=False))
            else:
                self.add_return(return_list, f'''{player} played {card.display()}, got {points} points and reached 31. Total is reset to 0.\n''', self.deck_look.get_hand_pic([[card]], show_index=False))
                
            self.add_return(return_list, f"Everyone is done pegging.\n")

            if(self.game.check_crib_joker() == False):
                await self.finished_pegging(return_list)
            else:
                self.add_return(return_list, f"Flipped card: {self.game.deck.get_flipped().display()}", self.deck_look.get_hand_pic([[self.game.deck.get_flipped()]], show_index=False))
                self.add_return(return_list, f"***{self.game.get_players()[self.game.crib_index%len(self.game.get_players())]} must choose which card to turn the joker in their crib into before game can proceed.***", self.deck_look.get_hand_pic([self.game.get_crib()], show_index=False))

        #If pegged out, end game
        if(self.game.get_winner() != None):
            return self.get_winner_string(self.game.get_winner(), return_list=return_list)

        return return_list
    
    async def finished_pegging(self, return_list):
        self.game.pegging_done()

        pic_list = [[self.game.deck.get_flipped()]]
        output_string = f"Flipped card: {self.game.deck.get_flipped().display()}\n"

        #Calculate points
        all_hands = self.game.get_hands()
        for player in self.game.get_players():
            index = (self.game.get_player_index(player) + self.game.get_players().index(self.game.get_crib_player()) + 1) % len(self.game.get_players())
            output_string += self.count_hand(self.game.get_players()[index])
            pic_list += [all_hands[index]]
            
            #Check for winner
            if(self.game.get_winner() != None):
                return self.get_winner_string(self.game.get_winner(), return_list=return_list)

        #Calculate crib
        output_string += self.count_crib()
        pic_list += [self.game.get_crib()]
        self.add_return(return_list, output_string, self.deck_look.get_hand_pic(pic_list, show_index=False))

        #Check for winner
        if(self.game.get_winner() != None):
            return self.get_winner_string(self.game.get_winner(), return_list=return_list)

        #Reset variables for the next round
        self.game.reset_round()

        #Update hand if applicable
        for player_index in range(len(self.game.get_players())):
            await self.update_hand(self.game.get_players()[player_index])

        #Finalize and send output_string to group chat
        return self.add_return(return_list, f"**Total Points**:\n{self.get_point_string()}\n" + self.get_start_string(player))
    
    def make_joker_parse(self, parse_str):
        #Split message into number and suit letter
        try:
            value_list = parse_str[1:].split()
            value = ''
            suit = ''

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

            return [value, suit]
        except:
            return [None, None]

    #Function to turn joker into another card
    async def make_joker(self, player, value, suit):
        return_list = []

        if player in self.game.get_players():
            #Split message into number and suit letter
            if (value == None) or (suit == None):
                return self.add_return(return_list, "Failed to parse joker message.")
            
            #Create card and get player index
            card = dk.Card(value, suit)

            if self.game.change_hand_joker(card, player) == True:
                #Update hand if applicable
                await self.update_hand(player)

                stats.access_field(stats.Cribbage, player, stats.Cribbage.times_changing_hand_joker, func=stats.increment)

                return self.add_return(return_list, f"Joker in hand has been made into {card.display()}.", self.deck_look.get_hand_pic([[card]], show_index=False))
                
            #Change flipped joker to specified card
            elif self.game.change_flipped_joker(card, player) == True:
                stats.access_field(stats.Cribbage, player, stats.Cribbage.times_changing_flipped_joker, func=stats.increment)
                if(card.value == dk.JACK):
                    self.add_return(return_list, f"Flipped joker has been made into {card.display()}.\n{self.game.get_players()[self.game.crib_index % len(self.game.get_players())]} gets nibs for 2.\nPegging will now begin with **{self.game.get_players()[self.game.pegging_index % len(self.game.get_players())]}**", self.deck_look.get_hand_pic([[card]], show_index=False))
                    
                    #Check for winner
                    if(self.game.get_winner() != None):
                        return self.get_winner_string(self.game.get_winner(), return_list=return_list)
                
                    return return_list
                else:
                    return self.add_return(return_list, f"Flipped joker has been made into {card.display()}.\nPegging will now begin with **{self.game.get_players()[self.game.pegging_index]}**", self.deck_look.get_hand_pic([[card]], show_index=False))
                
            #Change joker in crib to specified card
            elif self.game.change_crib_joker(card, player) == True:
                stats.access_field(stats.Cribbage, player, stats.Cribbage.times_changing_crib_joker, func=stats.increment)
                self.add_return(return_list, f"Joker in crib has been made into {card.display()}.", self.deck_look.get_hand_pic([[card]], show_index=False))
                await self.finished_pegging(return_list)
                return return_list

            return self.add_return(return_list, f"You need to have a joker in order to use this command, {player}.")
        
        return self.add_return(return_list, f"You need to be in the game to play, {player}. Use !join between games to join.")
    
    #Calculate hands, add points, and return a string with the details.
    def count_hand(self, player):
        #Get player index
        if player not in self.game.get_players():
            return False

        #Variable to hold output
        output_string = ""

        #Add points from hand
        [get_points, get_output] = self.game.calculate_hand(self.game.get_player_hand(player=player), self.game.deck.get_flipped())

        #Calculate stats/achievements
        if self.custom != True:
            if self.reverse == True:
                if self.joker == True:
                    if self.mega == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_joker_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_joker_mega_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_joker_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_joker_mega_hand, data=str(get_points))
                    elif self.standard == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_standard_joker_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_standard_joker_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_standard_joker_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_standard_joker_hand, data=str(get_points))
                else:
                    if self.mega == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_standard_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_standard_mega_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_standard_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_standard_mega_hand, data=str(get_points))
                    elif self.standard == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_standard_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_reverse_standard_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_standard_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_reverse_standard_hand, data=str(get_points))
            else:
                if self.joker == True:
                    if self.mega == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_joker_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_joker_mega_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_joker_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_joker_mega_hand, data=str(get_points))
                    elif self.standard == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_standard_joker_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_standard_joker_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_standard_joker_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_standard_joker_hand, data=str(get_points))
                else:
                    if self.mega == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_standard_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_standard_mega_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_standard_mega_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_standard_mega_hand, data=str(get_points))
                    elif self.standard == True:
                        if get_points < int(stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_standard_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.lowest_standard_hand, data=str(get_points))
                        if get_points > int(stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_standard_hand)):
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.highest_standard_hand, data=str(get_points))

        self.game.points[self.game.get_player_index(player)] += get_points

        #Send calculation to variable in game.py
        self.calc_string += f"**{player}'s Hand**:\n" + get_output + "\n\n"

        #Add data to group output
        output_string += f"{player}'s hand: {[hand_card.display() for hand_card in sorted(self.game.hands[self.game.get_player_index(player)], key=lambda x: x.to_int_runs())]} for {get_points} points.\n"

        return output_string

    def count_crib(self):
        #Calculate crib
        [get_points, get_output] = self.game.calculate_crib(self.game.crib, self.game.deck.flipped)
        self.game.points[self.game.crib_index % len(self.game.get_players())] += get_points
        output_string = f"{self.game.get_players()[self.game.crib_index % len(self.game.get_players())]}'s crib: {[crib_card.display() for crib_card in sorted(self.game.crib, key=lambda x: x.to_int_runs())]} for {get_points} points."
        
        #Send calculation to variable in game.py
        self.calc_string += f"**{self.game.get_players()[self.game.crib_index % len(self.game.get_players())]}'s Crib**:\n" + get_output + "\n\n"

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
        num_players = len(self.game.get_players())

        #Get the list of teams
        team_list = ""
        num_teams = num_players // self.game.team_size
        for team_num in range(num_teams):
            team_list += f"**Team {team_num}**: "
            for player in range(self.game.team_size):
                team_list += f"*{self.game.get_players()[player*num_teams + team_num]}*, "
            team_list = team_list[:-2] + "\n"

        return team_list

    #Ends the game and returns a string with point details.
    def get_winner_string(self, winner, show_hands=True, return_list=None):
        player_scores = ""
        player_hands = ""
        winner_string = winner

        #Shows the hands
        if(show_hands):
            #Make sure that backup_hands has been initialized
            if(len(self.game.backup_hands) == len(self.game.get_players())):
                player_hands += f"Flipped card is: {self.game.deck.get_flipped().display()}\n"
                for hand_index in range(len(self.game.get_players())):
                    player_hands += f"{self.game.get_players()[hand_index]}'s hand: {[card.display() for card in sorted(self.game.backup_hands[hand_index], key=lambda card:card.to_int_15s())]}\n"

            #Make sure that crib has been initialized
            if(len(self.game.crib) == self.game.crib_size):
                player_hands += f"{self.game.get_players()[self.game.crib_index%len(self.game.get_players())]}'s crib: {[card.display() for card in sorted(self.game.crib, key=lambda card:card.to_int_15s())]}\n"

        #Shows the ending point totals
        point_array = self.game.get_point_array()
        num_skunks = 0
        num_double_skunks = 0
        for point_index in range(len(point_array)):
            if(point_array[point_index] < (self.game.point_goal - self.game.skunk_length)):
                if self.game.team_size == 1: #If no teams, display based on name
                    #Sort out stats
                    if self.reverse == False:
                        if ((self.game.point_goal - point_array[point_index]) // self.game.skunk_length) > 1:
                            num_double_skunks += 1
                            stats.access_field(stats.Cribbage, self.game.get_players()[point_index], stats.Cribbage.total_times_double_skunked, func=stats.increment)
                        num_skunks += 1
                        stats.access_field(stats.Cribbage, self.game.get_players()[point_index], stats.Cribbage.total_times_skunked, func=stats.increment)

                        #Add details to string
                        player_scores += f"{self.game.get_players()[point_index]} got skunked x{(self.game.point_goal - point_array[point_index]) // self.game.skunk_length} at {point_array[point_index]} points.\n"
                else: #If teams, display by team
                    num_teams = len(self.game.get_players()) // self.game.team_size
                    player_scores += f"Team {point_index} ("
                    team_players = []
                    for player in range(num_teams):
                        player_scores += f"{self.game.get_players()[player*num_teams + point_index]}, "
                        team_players.append(self.game.get_players()[player*num_teams + point_index])

                    #Sort out stats
                    if self.reverse == False:
                        if ((self.game.point_goal - point_array[point_index]) // self.game.skunk_length) > 1:
                            num_double_skunks += 1
                            for player in team_players:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.total_times_double_skunked, func=stats.increment)
                        num_skunks += 1
                        for player in team_players:
                            stats.access_field(stats.Cribbage, player, stats.Cribbage.total_times_skunked, func=stats.increment)

                        #Add details to string
                        player_scores = player_scores[:-2] + f") got skunked x{(self.game.point_goal - point_array[point_index]) // self.game.skunk_length} at {point_array[point_index]} points.\n"
            else:
                if self.game.team_size == 1: #If no teams, display based on name
                    player_scores += f"{self.game.get_players()[point_index]} ended with {point_array[point_index]} points.\n"
                else: #If teams, display by team
                    num_teams = len(self.game.get_players()) // self.game.team_size
                    team = f"Team {point_index} ("
                    for player in range(self.game.team_size):
                        team += f"{self.game.get_players()[player*num_teams + point_index]}, "
                    team = team[:-2] + ")"

                    #If this team won, replace winner_string with team
                    if (point_array[point_index] >= self.game.point_goal) and (self.reverse == False):
                        winner_string = team
                    elif (point_array[point_index] < self.game.point_goal) and (self.reverse == True):
                        winner_string = team

                    #Add team and point data to output string player_scores
                    player_scores += team + f" ended with {point_array[point_index]} points.\n"

        #Sort out stats
        if self.game.team_size == 1:
            winning_players = [winner_string]
        else:
            winning_players = winner_string[8:-1].split(", ") #Remove "Team x (" from beginning and ")" from end
        
        for player_index in range(len(self.game.get_players())):
            player = self.game.get_players()[player_index]
            stats.access_field(stats.Cribbage, player, stats.Cribbage.total_points_scored, data=f"{int(stats.access_field(stats.Cribbage, player, stats.Cribbage.total_points_scored)) + self.game.points[player_index]}")
            if player not in winning_players:
                stats.access_field(stats.Cribbage, player, stats.Cribbage.total_losses, func=stats.increment)
                stats.access_field(stats.General, player, stats.General.total_losses, func=stats.increment)

                if self.custom == False:
                    if self.reverse == True:
                        if self.joker == True:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_joker_mega_losses, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_standard_joker_losses, func=stats.increment)
                        else:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_standard_mega_losses, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_standard_losses, func=stats.increment)
                    else:
                        if self.joker == True:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.joker_mega_losses, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.standard_joker_losses, func=stats.increment)
                        else:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.standard_mega_losses, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.standard_losses, func=stats.increment)
            else:
                stats.access_field(stats.Cribbage, player, stats.Cribbage.total_wins, func=stats.increment)
                stats.access_field(stats.General, player, stats.General.total_wins, func=stats.increment)

                if self.custom == False:
                    if self.reverse == True:
                        if self.joker == True:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_joker_mega_wins, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_standard_joker_wins, func=stats.increment)
                        else:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_standard_mega_wins, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.reverse_standard_wins, func=stats.increment)
                    else:
                        if self.joker == True:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.joker_mega_wins, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.standard_joker_wins, func=stats.increment)
                        else:
                            if self.mega == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.standard_mega_wins, func=stats.increment)
                            elif self.standard == True:
                                stats.access_field(stats.Cribbage, player, stats.Cribbage.standard_wins, func=stats.increment)

                for _ in range(num_skunks):
                    stats.access_field(stats.Cribbage, player, stats.Cribbage.total_skunks, func=stats.increment)
                for _ in range(num_double_skunks):
                    stats.access_field(stats.Cribbage, player, stats.Cribbage.total_double_skunks, func=stats.increment)

        #Return sequence
        if return_list != None:
            self.add_return(return_list, player_hands, self.deck_look.get_hand_pic(self.game.backup_hands + [self.game.get_crib()], show_index=False))
            self.game.end_game()
            return self.add_return(return_list, player_scores + f"{winner_string} has won the game! Everything will now be reset.")
        else:
            self.game.end_game()
            return self.add_return(return_list, player_hands + player_scores + f"{winner_string} has won the game! Everything will now be reset.")

    #Returns a string with each team and the number of points they have
    def get_point_string(self, always_solo=False):
        output_string = ""

        #If playing alone, don't have team names
        #Else, print out teams and points for team
        if self.game.team_size == 1 or always_solo == True:
            for player_index in range(len(self.game.get_players())):
                output_string += f"*{self.game.get_players()[player_index]}* has {self.game.points[player_index]} points.\n"
        else:
            point_count = 0
            num_teams = len(self.game.get_players()) // self.game.team_size

            for team_num in range(num_teams):
                output_string += f"**Team {team_num}** ("
                for player in range(self.game.team_size):
                    point_count += self.game.points[player*num_teams + team_num]
                    output_string += f"*{self.game.get_players()[player*num_teams + team_num]}*, "
                output_string = output_string[:-2] + f") has {point_count} points.\n"
                point_count = 0

        return output_string[:-1]
        
    #Returns the string to be displayed when the game is started
    #NOTE: This function overrides the one defined in Game_Print
    def get_start_string(self, _player) -> str:
        output_str = f'''\nThrow {self.game.throw_count} cards into **{self.game.get_crib_player()}**'s crib.\n*Use "/h" or "/hand" to see your hand.*'''
        if self.game.get_num_jokers() != 0:
            output_str += f'''\n***There are {self.game.get_num_jokers()} joker(s) that must be transformed before players can throw cards into the crib.***'''
        return output_str
    
    #Returns the string to be displayed when the game is ended
    #NOTE: This function overrides the one defined in Game_Print
    def get_end_string(self, _player) -> str:
        #Find winner based on number of points
        winner_index = 0
        for point_index in range(1, len(self.game.get_players())):
            if(self.game.points[point_index] > self.game.points[winner_index]):
                winner_index = point_index
        
        #Get string based on current winner
        return self.get_winner_string(self.game.get_players()[winner_index])