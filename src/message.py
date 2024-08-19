#Foreign imports
import re
import copy
import discord
import os

#Local imports
import Games.Backend.Helper.Cribbage.game as game
import Games.deck as dk

hand_messages = [] #Variable to hold most recent hand message so that it can be modified as needed

HELP_MESSAGE = '''The bot knows the following commands:
    ***General***:
      Start Game:
        '**!join**': Let the bot know that you'd like to play cribbage.
        '**!unjoin**': Let the bot know that you changed your mind and don't want to play.
        '**!start**': Starts a game with all players who have done !join
        '**![0-9]+**': Plays the card with the given index.

      Private Commands:
        '**/hand**', '**/h**': View your hand.

      Public Commands:
        '**/spectate**': View hands of all players (only works if not participating in the game).
        '**/calcs**': View how points were obtained in the previous round (hands and crib).
        '**/points**': View current number of points each PLAYER has at current point in time.
        '**/team_points**': View current number of points each team has at current point in time.
        '**/help**': Display orders that the bot can execute.
        '**/rules**': Show the rules of cribbage.

      End Early:
        '**!end**': All players must type in the command to end the game early.

      Other:
        '**!treasurelady**', '**!tl**': Change role to Treasure Lady.
        '**!garbageman**', '**!gm**': Change role to Garbage Man.

    ***Cribbage***:
      Start Game:
        '**!cribbage**': Create a game of Cribbage.
        '**!standard**': Play a regular game of cribbage (default).
        '**!mega**': Play a game of mega hand (8 cards, twice as many points to win).
        '**!joker**': Play a game of joker mode (2 wild cards).
        '**![A2-9JQK]|10 [HDCS]**': Used to transform the joker into the desired card.
        '**!teams [0-9]+**': Splits players into teams with the specified number of players on each team. Will automatically start the game.

      Private Commands:
        '**/thrown**': View the cards you've most recently thrown away.'''


async def process_message(msg):
    try:
        bot_feedback = await handle_user_messages(msg)
        if(len(bot_feedback) > 0):
            for item in bot_feedback:
                if(item[1] == None): #Not a file
                    await msg.channel.send(item[0])
                else:
                    await msg.channel.send(content=item[0], file=discord.File(item[1]))
    except Exception as error:
        print(error)

def add_return(return_list, return_string, file=None, index=None):
    if(index == None):
        index = len(return_list)

    if(index >= len(return_list)):
        return_list.append([return_string, file])
    elif(index < len(return_list)):
        return_list.insert(index, [return_string, file])

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