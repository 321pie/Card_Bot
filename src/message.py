#Foreign imports
import re
import discord

#Local imports
from Games.game_print import Game_Print as gp
from Games.Cribbage.cribbage_print import Cribbage_Print
from Games.Juiced.juiced_print import Juiced_Print
from Games.Test.test_print import Test_Print

active_games:list[gp] = []

cur_game:gp = None

async def process_message(msg):
    try:
        bot_feedback = await handle_user_messages(msg)
        if(len(bot_feedback) > 0):
            for item in bot_feedback:
                if(item[1] == None): #Not a file
                    await msg.channel.send(item[0])
                else:
                    await msg.channel.send(content=item[0], file=discord.File(fp=item[1], filename="Pic.png"))
    except Exception as error:
        print(error)

async def handle_user_messages(msg):
    global active_games
    global cur_game

    message = msg.content.lower()
    return_list = []

    #Weed out excess messages
    if len(message) == 0 or message[0] != '!':
        return return_list
    
    player_in_game:bool = False
    player = msg.author.name
    
    #Commands from an active game
    for active_game in active_games:
        if player in active_game.get_players():
            player_in_game = True
            return_var = await run_commands(player, message, active_game)
            if return_var != None:
                #Remove game from list if ended
                if active_game.is_started() == False:
                    active_games.remove(active_game)

                return return_var
            else:
                break #Player can only be in one game at a time
                    
    #Commands from game that is being created (don't allow people already in a game)
    if (cur_game != None) and (player_in_game == False):
        return_var = await run_commands(player, message, cur_game)
        if return_var != None:
            if cur_game.is_started():
                active_games.append(cur_game)
                cur_game = None

            return return_var
    
    #Commands to add a game
    if message == "!cribbage" or message == "!cr":
        return make_cribbage(player)
    elif message == "!juiced" or message == "!jc":
        return make_juiced(player)
    elif message == "!test":
        return make_test(player)
    
    #Roles
    elif message == '!db' or message == '!dumpsterboy':
        return await give_role(msg.author, "Dumpster Boy")
    elif message == '!gg' or message == '!glamourgirl':
        return await give_role(msg.author, "Glamour Girl")
    elif message == '!gm' or message == '!garbageman':
        return await give_role(msg.author, "Garbage Man")
    elif message == '!tl' or message == '!treasurelady':
        return await give_role(msg.author, "Treasure Lady")
    
    #Default case (orders bot doesn't understand)
    return return_list

#Makes a game of Cribbage to be joined
def make_cribbage(player):
    global cur_game
    
    if cur_game == None:
        cur_game = Cribbage_Print()
        return gp().add_return([], f"{player} has created a Cribbage game. Use **!join** to join it!")
    else:
        return gp().add_return([], f"Sorry, {player}. You need to wait until the current game is started to create another one.")
    
#Makes a game of Juiced to be joined
def make_juiced(player):
    global cur_game
    
    if cur_game == None:
        cur_game = Juiced_Print()
        return gp().add_return([], f"{player} has created a Juiced game. Use **!join** to join it!")
    else:
        return gp().add_return([], f"Sorry, {player}. You need to wait until the current game is started to create another one.")
    
#Makes a game of Test to be joined
def make_test(player):
    global cur_game
    
    if cur_game == None:
        cur_game = Test_Print()
        return gp().add_return([], f"{player} has created a Test game. Use **!join** to join it!")
    else:
        return gp().add_return([], f"Sorry, {player}. You need to wait until the current game is started to create another one.")

#Give role to user
async def give_role(member, role):
    await member.edit(roles=[discord.utils.get(member.guild.roles, name=role), discord.utils.get(member.guild.roles, name="Ping if Playing")])
    return gp().add_return([], member.name + ' is now a ' + role + '!')

#Runs the command if needed or returns None
async def run_commands(player, message, game):
    for command in game.commands:
        if re.fullmatch(command, message) != None:
            func_list = game.commands[command]
            if len(func_list) > 1:
                return await func_list[0](player, *(func_list[1](message)))
            else:
                return await func_list[0](player)
                
    return None
    