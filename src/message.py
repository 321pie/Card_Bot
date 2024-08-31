#Foreign imports
import re
import discord

#Local imports
from Games.game_print import Game_Print as gp
from Games.Cribbage.cribbage_print import Cribbage_Print

active_games:list[gp] = []

cur_game:gp = None

HELP_MESSAGE = '''The bot knows the following commands:
    ***General***:
      Start Game:
        '**!join**': Let the bot know that you'd like to play cribbage.
        '**!unjoin**': Let the bot know that you changed your mind and don't want to play.
        '**!start**': Starts a game with all players who have done !join.
        '**!end**': Ends a game once all players have entered the command.
        '**![0-9]+**': Plays the card with the given index.

      Private Commands:
        '**/hand**': View your hand.

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
        '**!goal [0-9]+**': Set the amount of points needed to reach the goal to the provided number.
        '**!skunk [0-9]+**': Set the skunk interval (default=30) to the provided number.

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
    global active_games
    global cur_game

    message = msg.content.lower()
    return_list = []

    #Weed out excess messages
    if(message[0] != '!'):
        return return_list
    
    player_in_game:bool = False
    
    #Commands from an active game
    for active_game in active_games:
        if msg.author in active_game.get_players():
            player_in_game = True
            return_var = await run_commands(msg.author, message, active_game)
            if return_var != None:
                #Remove game from list if ended
                if active_game.is_started() == False:
                    active_games.remove(active_game)

                return return_var
            else:
                break #Player can only be in one game at a time
                    
    #Commands from game that is being created (don't allow people already in a game)
    if (cur_game != None) and (player_in_game == False):
        return_var = await run_commands(msg.author, message, cur_game)
        if return_var != None:
            if cur_game.is_started():
                active_games.append(cur_game)
                cur_game = None

            return return_var
    
    #Commands to add a game
    if message == "!cribbage":
        return make_cribbage(msg.author)
    
    #Roles
    elif(message == '!gm' or message == '!garbageman'):
        return await give_role(msg.author, "Garbage Man")
    elif(message == '!tl' or message == '!treasurelady'):
        return await give_role(msg.author, "Treasure Lady")
    
    #Default case (orders bot doesn't understand)
    return return_list

def make_cribbage(player):
    global cur_game
    
    if cur_game == None:
        cur_game = Cribbage_Print()
        return add_return([], f"{player.name} has created a cribbage game. Use **!join** to join it!")
    else:
        return add_return([], f"Sorry, {player.name}. You need to wait until the current game is started to create another one.")

#Give role to user
async def give_role(member, role):
    await member.edit(roles=[discord.utils.get(member.guild.roles, name=role)])
    return add_return([], member.name + ' is now a ' + role + '!')

async def run_commands(player, message, game):
    for command in game.commands:
        if re.fullmatch(command, message) != None:
            func_list = game.commands[command]
            if len(func_list) > 1:
                return await func_list[0](player, *(func_list[1](message)))
            else:
                return await func_list[0](player)
                
    return None
    