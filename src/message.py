#Foreign imports
import re
import discord
import os

#Local imports
import Games.game as gm
from Games.Cribbage.cribbage_print import Cribbage_Print

active_games = []

cur_game = None

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
    
    #Commands from an active game
    for active_game in active_games:
        if msg.author in active_game.get_players():
            for command in active_game.commands:
                if re.search(command, message) != None:
                    func_list = active_game.commands[command]
                    if len(func_list) > 1:
                        return func_list[0](msg.author, *func_list[1])
                    else:
                        return func_list[0](msg.author)
                    
    if re.search('^!teams [0-9]+$', message) != None:
        return await form_teams(msg.author, int(message[7:]))
    
    #Commands to add a game
    elif message == "!cribbage":
        return await make_cribbage(msg.author)
    
    #Roles
    elif(message == '!gm' or message == '!garbageman'):
        return await give_role(msg.author, "Garbage Man")
    elif(message == '!tl' or message == '!treasurelady'):
        return await give_role(msg.author, "Treasure Lady")
    
    #Default case (orders bot doesn't understand)
    return return_list


    
# #Starts the game
# async def start(player):
#     global cur_game

#     return_list = []

#     #Start game
#     if(player in cur_game.game.players):
#         #Initiate game vars
#         return_list = await start(player)
#         active_games.append(cur_game)
#         cur_game = None
        
#     return return_list

# #Function to form teams of two if applicable
# async def form_teams(player, count):
#     created, return_list = []

#     #If teams are even, start game
#     if (cur_game.create_teams(count) == True):
#         return_list = await start(player)

#         #Add the teams to be printed before the start returns (index=0)
#         add_return(return_list, f"Teams of {count} have been formed:\n{game.get_teams_string()}", index=0)
#     else:
#         add_return(return_list, "There must be an equal number of players on each team in order to form teams.")
    
#     return return_list

def make_cribbage(player):
    global cur_game
    
    if cur_game != None:
        return add_return([], f"Sorry, {player.name}. You need to wait until the current game is created")
    else:
        cur_game = Cribbage_Print()

#Give role to user
async def give_role(member, role):
    await member.edit(roles=[discord.utils.get(member.guild.roles, name=role)])
    return add_return([], member.name + ' is now a ' + role + '!')

# def end(player):
#     if(player in game.players):
#         #Get player index
#         try:
#             player_index = game.players.index(player)
#         except:
#             return ''

#         if(game.game_started == True):
#             game.end[player_index] = True
            
#             #Check to see if all players agree
#             game_over = True
#             for ii in range(len(game.end)):
#                 if(game.end[ii] == False):
#                     game_over = False
#                     break

#             if(game_over == True):
#                 winner = 0
#                 for point_index in range(1, len(game.points)):
#                     if(game.points[point_index] > game.points[winner]):
#                         winner = point_index
#                 winner = game.players[winner]

#                 return add_return([], f"Game has been ended early by unanimous vote.\n" + game.get_winner_string(winner))
#             else:
#                 return add_return([], f"{player.name} wants to end the game early. Type !end to agree.")
#         else:
#             return add_return([], f"You can't end a game that hasn't started yet, {player.name}. Use !unjoin to leave queue.")
        
#     return []

