#Foreign imports
import re
import copy
import discord
import os

#Local imports
import game
import deck as dk

hand_messages = [] #Variable to hold most recent hand message so that it can be modified as needed

def help_message():
    return '''The bot knows the following commands:

    Cribbage:
      Start Game:
        '**!join**': Let the bot know that you'd like to play cribbage.
        '**!unjoin**': Let the bot know that you changed your mind and don't want to play.
        '**!standard**': Play a regular game of cribbage (default).
        '**!mega**': Play a game of mega hand (8 cards, twice as many points to win).
        '**!joker**': Play a game of joker mode (2 wild cards).
        '**![A2-9JQK]|10 [HDCS]**': Used to transform the joker into the desired card.
        '**!start**': Starts a game with up to 8 players who have done !join.
        '**!teams [0-9]+**': Splits players into teams with the specified number of players on each team. Will automatically start the game.

      Private Commands:
        '**/hand**', '**/h**': View your hand.
        '**/thrown**': View the cards you've most recently thrown away.

      Public Commands:
        '**/spectate**': View hands of all players (only works if not participating in the game).
        '**/calcs**': View how points were obtained in the previous round (hands and crib).
        '**/points**': View current number of points each PLAYER has at current point in time.
        '**/team_points**': View current number of points each team has at current point in time.
        '**/help**': Display orders that the bot can execute.
        '**/rules**': Show the rules of cribbage.

      Throw Into Crib:
        '**![0-9]+**': Puts the card with the given index into the current crib.

      Counting:
        '**![0-9]+**': Plays the card with the given index.

      End Early:
        '**!end**': All players must type in the command to end the game early.

    Other:
    '**!treasurelady**', '**!tl**': Change role to Treasure Lady.
    '**!garbageman**', '**!gm**': Change role to Garbage Man.'''


async def process_message(msg):
    try:
        bot_feedback = await handle_user_messages(msg)
        if(len(bot_feedback) > 0):
            for item in bot_feedback:
                if(item[1] == False): #Not a file
                    await msg.channel.send(item[0])
                else:
                    #Check for valid path
                    if not os.path.exists(os.path.dirname(item[0])):
                        print(f"Invalid path: {item[0]}")
                        return
                    await msg.channel.send(content=f"Flipped card: {game.deck.get_flipped().display()}", file=discord.File(item[0]))
                    os.remove(item[0])

    except Exception as error:
        print(error)

def add_return(return_list, return_string, isFile=False, index=None):
    if(index == None):
        index = len(return_list)

    if(index >= len(return_list)):
        return_list.append([return_string, isFile])
    elif(index < len(return_list)):
        return_list.insert(index, [return_string, isFile])

    return return_list

async def handle_user_messages(msg):
    message = msg.content.lower()
    return_list = []

    #Weed out excess messages
    if(message[0] != '!'):
        return return_list
    
    #Cribbage commands
    elif(re.search('^![0-9]+$', message) != None):
        return await card_select(msg.author, int(message[1:]))
    elif(message == '!join' or message == '!jion'):
        return join(msg.author)
    elif(message == '!unjoin' or message == '!unjion'):
        return unjoin(msg.author)
    elif(message == '!standard'):
        return standard(msg.author)
    elif(message == '!mega'):
        return mega(msg.author)
    elif(message == '!joker'):
        return joker(msg.author)
    elif(message == '!start'):
        return await start(msg.author)
    elif(re.search('^!teams [0-9]+$', message) != None):
        return await form_teams(msg.author, int(message[7:]))
    elif(re.search('^![a2-9jqk]|10 [hdcs]$', message) != None):
        return await make_joker(msg.author, message)
    elif(message == '!end'):
        return end(msg.author)
    
    #Roles
    elif(message == '!gm' or message == '!garbageman'):
        return await give_role(msg.author, "Garbage Man")
    elif(message == '!tl' or message == '!treasurelady'):
        return await give_role(msg.author, "Treasure Lady")
    
    #Default case (orders bot doesn't understand)
    return return_list

#Updates a player's hand if applicable.
async def update_hand(author):
    if(hand_messages[game.players.index(author)] != None):
        hand_pic = await game.get_hand_pic(game.players.index(author))
        await hand_messages[game.players.index(author)].edit_original_response(attachments=[discord.File(hand_pic)])
        os.remove(hand_pic)

def join(author):
    return_list = []

    if(game.game_started == False):
        #Add person to player list and send confirmation message
        if(author not in game.players):
            if(len(game.players) < 8):
                game.players.append(author)
                return add_return(return_list, f"Welcome to the game, {author.name}! Type !start to begin game with {len(game.players)} players.")
            else:
                return add_return(return_list, f"Sorry, {author.name}. This game already has 8 players {[player.name for player in game.players]}. If this is wrong, type !unjoinall.")
        else:
            return add_return(return_list, f"You've already queued for this game, {author.name}. Type !start to begin game with {len(game.players)} players.")
        
    return return_list
    
def unjoin(author):
    return_list = []

    if(game.game_started == False):
        #Remove person from player list and send confirmation message
        if(author in game.players):
            game.players.remove(author)
            return add_return(return_list, f"So long, {author.name}.")
        else:
            return add_return(return_list, f"You never queued for this game, {author.name}.")
        
    return return_list
    
#Changes game mode to standard
def standard(author):
    return_list = []

    if(game.game_started == False):
        game.end_game()
        return add_return(return_list, f"{author.name} has changed game mode to standard. Consider giving !mega and !joker a try, or use !start to begin.")
    
    return return_list

#Changes game mode to mega hand
def mega(author):
    return_list = []

    if(game.game_started == False):
        game.mega_hand()
        return add_return(return_list, f"{author.name} has changed game mode to mega. Use !standard to play regular cribbage or !start to begin.")
    
    return return_list

#Changes game mode to joker mode
def joker(author):
    return_list = []

    if(game.game_started == False):
        game.joker_mode()
        return add_return(return_list, f"{author.name} has changed game mode to joker mode. Use !standard to play regular cribbage or !start to begin.")
    
    return return_list
    
#Starts the game
async def start(author):
    return_list = []

    if(game.game_started == False):
        #Start game
        if(author in game.players):
            #Initiate game vars
            game.start_game()
            for _ in range(len(game.players)):
                hand_messages.append(None)

            return add_return(return_list, f'''{author.name} has started the game.\nThrow {game.throw_count} card(s) into **{game.players[game.crib_index % len(game.players)]}**'s crib.\n*Use "/hand" to see your hand.*''')
        else:
            return add_return(return_list, f"You can't start a game you aren't queued for, {author.name}.")
        
    return return_list

#Function to form teams of two if applicable
async def form_teams(author, count):
    return_list = []

    #If teams are even, start game
    if (game.create_teams(count) == True):
        return_list = await start(author)

        #Add the teams to be printed before the start returns (index=0)
        add_return(return_list, f"Teams of {count} have been formed:\n{game.get_teams_string()}", index=0)
    else:
        add_return(return_list, "There must be an equal number of players on each team in order to form teams.")
    
    return return_list

#Function to turn joker into another card
async def make_joker(author, message):
    return_list = []

    if author in game.players:
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
            return add_return(return_list, "Failed to parse joker message.")
        
        #Create card and get player index
        card = dk.Card(value, suit)

        if game.change_hand_joker(card, author) == True:
            #Update hand if applicable
            await update_hand(author)

            return add_return(return_list, f"Joker in hand has been made into {card.display()}.")
            
        #Change flipped joker to specified card
        elif game.change_flipped_joker(card, author) == True:
            if(card.value == dk.JACK):
                add_return(return_list, f"Flipped joker has been made into {card.display()}.\n{game.players[game.crib_index % len(game.players)]} gets nibs for 2.\nPegging will now begin with **{game.players[game.pegging_index]}**")
                
                #Check for winner
                if(game.get_winner() != None):
                    return add_return(return_list, game.get_winner_string(game.get_winner()))
            
                return return_list
            else:
                return add_return(return_list, f"Flipped joker has been made into {card.display()}.\nPegging will now begin with **{game.players[game.pegging_index]}**")
            
        #Change joker in crib to specified card
        elif game.change_crib_joker(card, author) == True:
            add_return(return_list, f"Joker in crib has been made into {card.display()}.")
            await finished_pegging(return_list)
            return return_list

        return add_return(return_list, f"You need to have a joker in order to use this command, {author.name}.")
    
    return add_return(return_list, f"You need to be in the game to play, {author.name}. Use !join between games to join.")
        
async def card_select(author, card_index):
    #Get player index
    try:
        player_index = game.players.index(author)
    except:
        return []

    if(author in game.players):
        #Check for valid index or return
        if(card_index >= len(game.hands[player_index]) or card_index < 0):
            return []

        if(game.game_started == True):
            if(game.throw_away_phase == True):
                return await throw_away_phase_func(author, card_index)
            elif(game.pegging_phase == True):
                return await pegging_phase_func(author, card_index)

    return []

async def throw_away_phase_func(author, card_index):
    return_list = []

    #Don't do anything if player not in game.
    if(author not in game.players):
        return return_list
    
    #If player has joker card (joker mode), force them to make joker something before anybody throws.
    if game.check_hand_joker() != None:
        return add_return(return_list, f"You can't throw away cards until {game.check_hand_joker().name} has chosen which card to turn their joker into.")

    #If throwing away a card fails, alert player.
    if(game.throw_away_card(author, card_index) == False):
        return add_return(return_list, f"You have already thrown away the required number of cards, {author.name}.")

    #Update hand if applicable.
    await update_hand(author)

    #Check if everyone is done. If not, return. Else, get flipped card and begin pegging round.
    if(game.is_finished_throwing(author)):
        if(not game.everyone_is_finished_throwing()):
            add_return(return_list, f'''{author.name} has finished putting cards in the crib.''')
            return return_list
        else:
            game.prepare_pegging()

            #Add display text
            flipped = game.deck.get_flipped()
            if(flipped.value != dk.JACK):
                add_return(return_list, f'''{author.name} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.''')
            else:
                add_return(return_list, f'''{author.name} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.\n{game.players[game.crib_index % len(game.players)]} gets nibs for 2.''')
            
            #Check for winner
            if(game.get_winner() != None):
                return add_return(return_list, game.get_winner_string(game.get_winner()))
            
            #Check for flipped joker
            if(flipped.value == dk.JOKER):
                add_return(return_list, f"***{game.players[game.crib_index % len(game.players)].name} must choose which card to turn the flipped joker into before game can proceed.***")
            else:
                add_return(return_list, f"Pegging will now begin with **{game.players[game.pegging_index]}**.")
        
    return return_list

async def finished_pegging(return_list):
    game.pegging_done()

    output_string = f"Flipped card: {game.deck.get_flipped().display()}\n"

    #Calculate points
    for player_index in range(len(game.players)):
        output_string += game.count_hand(game.players[player_index])
        
        #Check for winner
        if(game.get_winner() != None):
            return add_return(return_list, game.get_winner_string(game.get_winner()))

    #Calculate crib
    output_string += game.count_crib()

    #Check for winner
    if(game.get_winner() != None):
        return add_return(return_list, game.get_winner_string(game.get_winner()))

    #Reset variables for the next round
    game.reset_round()

    #Update hand if applicable
    for player_index in range(len(game.players)):
        await update_hand(game.players[player_index])

    #Finalize and send output_string to group chat
    output_string += f'''\nThrow {game.throw_count} cards into **{game.players[game.crib_index % len(game.players)]}**'s crib.\n*Use "/h" or "/hand" to see your hand.*'''

    return add_return(return_list, output_string)

async def pegging_phase_func(author, card_index):
    return_list = []

    peg_vars = game.peg(author, card_index)
    if(peg_vars == None):
        #If pegged out, end game
        if(game.get_winner() != None):
            return add_return(return_list, game.get_winner_string(game.get_winner()))
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
                add_return(return_list, f'''{author.name} played {card.display()}, gaining {points} points and bringing the total to {cur_sum}.\nIt is now **{next_player}**'s turn to play.''')
            else:
                add_return(return_list, f'''{author.name} played {card.display()}, bringing the total to {cur_sum}.\nIt is now **{next_player}**'s turn to play.''')
        else:
            if(last_sum == 31):
                add_return(return_list, f'''{author.name} played {card.display()}, got {points} points and reached 31. Total is reset to 0.\nIt is now **{next_player}**'s turn to play.''')
            else:
                add_return(return_list, f'''{author.name} played {card.display()}, got {points} point(s) including last card. Total is reset to 0.\nIt is now **{next_player}**'s turn to play.''')

        #If player is out of cards, add message to print. Else, update hand.
        if(cur_player_hand_size != 0):
            await update_hand(author)
        else:
            add_return(return_list, f"{author.name} has played their last card.", index=0)
    else:
        #Prepare for next round
        my_sum = game.pegging_done()

        #Add last card data to 
        if(my_sum != 31):
            add_return(return_list, f'''{author.name} played {card.display()}, got {points} point(s) including last card. Total is reset to 0.\n''')
        else:
            add_return(return_list, f'''{author.name} played {card.display()}, got {points} points and reached 31. Total is reset to 0.\n''')
            
        add_return(return_list, f"Everyone is done pegging.\n")
        
        if(game.check_crib_joker() == False):
            await finished_pegging(return_list)
        else:
            add_return(return_list, f"***{game.players[game.crib_index % len(game.players)].name} must choose which card to turn the joker in their crib into before game can proceed.***")
            hand_pic = await game.get_hand_pic(-1)
            add_return(return_list, hand_pic, isFile=True)

    #If pegged out, end game
    if(game.get_winner() != None):
        return add_return(return_list, game.get_winner_string(game.get_winner()))

    return return_list

def end(author):
    if(author in game.players):
        #Get player index
        try:
            player_index = game.players.index(author)
        except:
            return ''

        if(game.game_started == True):
            game.end[player_index] = True
            
            #Check to see if all players agree
            game_over = True
            for ii in range(len(game.end)):
                if(game.end[ii] == False):
                    game_over = False
                    break

            if(game_over == True):
                winner = 0
                for point_index in range(1, len(game.points)):
                    if(game.points[point_index] > game.points[winner]):
                        winner = point_index
                winner = game.players[winner]

                return add_return([], f"Game has been ended early by unanimous vote.\n" + game.get_winner_string(winner))
            else:
                return add_return([], f"{author.name} wants to end the game early. Type !end to agree.")
        else:
            return add_return([], f"You can't end a game that hasn't started yet, {author.name}. Use !unjoin to leave queue.")
        
    return []

#Give role to user
async def give_role(member, role):
    await member.edit(roles=[discord.utils.get(member.guild.roles, name=role)])
    return add_return([], member.name + ' is now a ' + role + '!')