#Foreign imports
import re
import discord

#Local imports
from Games.Cribbage.cribbage_print import Cribbage_Print
from Games.game_print import Game_Print as gp
from Games.Jeopardy.jeopardy_print import Jeopardy_Print
from Games.Juiced.juiced_print import Juiced_Print
import Games.Minesweeper.minesweeper as minesweeper
from Games.Regicide.regicide_print import Regicide_Print
import Games.stats as stats
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
    stats.add_player(player)
    
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
    elif message == "!jeopardy" or message == "!jp":
        return make_jeopardy(player)
    elif message == "!regicide" or message == "!reg":
        return make_regicide(player)
    elif message == "!test":
        return make_test(player)
    
    #Commands to output a minigame
    elif message == "!minesweeper" or message == "!ms":
        return gp().add_return([], minesweeper.init_minesweeper())
    elif (re.fullmatch("^!ms [1-9] [1-9] ([1-9]|10)$", message) != None) or (re.fullmatch("^!minesweeper [1-9] [1-9] ([1-9]|10)$", message) != None):
        return gp().add_return([], minesweeper.init_minesweeper(*message.split(" ")[1:]))
    
    #Roles
    elif message == '!db' or message == '!dumpsterboy':
        stats.access_field(stats.General, player, stats.General.times_becoming_db, func=stats.increment)
        return await change_gender_role(msg.author, "Dumpster Boy")
    elif message == '!gg' or message == '!glamourgirl':
        stats.access_field(stats.General, player, stats.General.times_becoming_gg, func=stats.increment)
        return await change_gender_role(msg.author, "Glamour Girl")
    elif message == '!gm' or message == '!garbageman':
        stats.access_field(stats.General, player, stats.General.times_becoming_gm, func=stats.increment)
        return await change_gender_role(msg.author, "Garbage Man")
    elif message == '!tl' or message == '!treasurelady':
        stats.access_field(stats.General, player, stats.General.times_becoming_tl, func=stats.increment)
        return await change_gender_role(msg.author, "Treasure Lady")
    
    elif message == '!ping':
        return await toggle_role(msg.author, "Ping if Playing")
    
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
    
#Makes a game of Jeopardy to be joined
def make_jeopardy(player):
    global cur_game
    
    if cur_game == None:
        cur_game = Jeopardy_Print()
        return gp().add_return([], f"{player} has created a Jeopardy game. Use **!join** to join it!")
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
    
#Makes a game of Regicide to be joined
def make_regicide(player):
    global cur_game
    
    if cur_game == None:
        cur_game = Regicide_Print()
        return gp().add_return([], f"{player} has created a Regicide game. Use **!join** to join it!")
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

#Toggle role for user
async def toggle_role(member, role_name):
    #If user has role, delete it from user. Else, give user the role
    role = discord.utils.get(member.guild.roles, name=role_name)
    if role in member.roles:
        await member.remove_roles(role)

        return gp().add_return([], member.name + ' is no longer a ' + role_name + '!')
    else:
        await member.add_roles(role)

    return gp().add_return([], member.name + ' is now a ' + role_name + '!')

async def change_gender_role(member, role_name):
    #Intialize gender roles and delete current (only one gender role at a time)
    gender_roles = [discord.utils.get(member.guild.roles, name="Treasure Lady"), discord.utils.get(member.guild.roles, name="Glamour Girl"), discord.utils.get(member.guild.roles, name="Dumpster Boy"), discord.utils.get(member.guild.roles, name="Garbage Man")]
    for role in gender_roles:
        if role in member.roles:
            await member.remove_roles(role)

            #If already in requested role, then toggle off
            if role.name == role_name:
                return gp().add_return([], member.name + ' is no longer a ' + role_name + '!')

    #Add requested gender role
    await member.add_roles(discord.utils.get(member.guild.roles, name=role_name))

    return gp().add_return([], member.name + ' is now a ' + role_name + '!')

#Runs the command if needed or returns None
async def run_commands(player, message, game):
    for command in game.commands:
        if re.fullmatch(command, message) != None:
            func_list = game.commands[command]
            if len(func_list) > 1:
                print(*(func_list[1](message)))
                return await func_list[0](player, *(func_list[1](message)))
            else:
                return await func_list[0](player)
                
    return None