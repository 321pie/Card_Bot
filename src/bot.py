###########################################################
# File: bot.py
#
# Authors: Andrew Rice, Bryce Schultz
# Date: 4/7/2024
#
# Description: This file contains the main bot loop.
###########################################################

#Foreign imports
import discord
import os
import copy

#Local imports
import message
import credentials
import format
import game

spectators = []
spectator_messages = []

def run_bot():
    # Get token from credentials.json file
    discord_token = credentials.load_from_file('credentials.json')

    # If the token is None, exit.
    if discord_token == None:
        exit(1)

    # Create a discord client
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)

    #Sends picture of hand to user and adds hand to message.hand_messages for later reference
    @tree.command(name="hand", description="Get your current hand")
    async def hand_command(interaction):
        try:
            hand_pic = await game.get_hand_pic(game.players.index(interaction.user))
            await interaction.response.send_message(content="Number in center of card is index.", file=discord.File(hand_pic), ephemeral=True)
            os.remove(hand_pic)
        except:
            await interaction.response.send_message("You need to !join and !start before you can get your hand.", ephemeral=True)

        try:
            #Delete old ephemeral message and create new one
            if(message.hand_messages[game.players.index(interaction.user)] != None):
                await message.hand_messages[game.players.index(interaction.user)].delete_original_response()
            message.hand_messages[game.players.index(interaction.user)] = interaction
        except:
            pass

    #Sends calculations of most recent hand(s)/crib
    @tree.command(name="calcs", description="Get the most recent hand calcs")
    async def calc_command(interaction):
        if game.calc_string == "":
            await interaction.response.send_message("You need to finish a round before you can see the hand values.", ephemeral=True)
        else:
            await interaction.response.send_message(game.calc_string, ephemeral=True)

    #Sends the rules of cribbage
    @tree.command(name="rules", description='''See the rules.''')
    async def rules_command(interaction):
        await interaction.response.send_message(content="Rules outlined below.", file=discord.File(game.get_path("rules.txt")), ephemeral=True)

    #Sends each player's point total regardless of teams
    @tree.command(name="points", description="See each player's point totals.")
    async def point_command(interaction):
        if game.game_started == False:
            await interaction.response.send_message("Nobody is currently playing, so no points.", ephemeral=True)
        else:
            await interaction.response.send_message(game.get_point_string(True), ephemeral=True)

    #Sends each player's or team's point total
    @tree.command(name="team_points", description='''See team point totals (same as "/points" if no teams).''')
    async def team_point_command(interaction):
        if game.game_started == False:
            await interaction.response.send_message("No game currently happening, so no points.", ephemeral=True)
        else:
            await interaction.response.send_message(game.get_point_string(), ephemeral=True)

    #Sends every player's hand if player not in game
    @tree.command(name="spectate", description='''See every players' hands.''')
    async def spectate_command(interaction):
        player_text = ""
        for player in game.players:
            player_text += player.name + ", "
        player_text = player_text[:-2] #Remove ", " from end
        hand_pic = await game.get_all_hand_pics()

        if interaction.user in game.players:
            #Free discord.File variable so that card art can be deleted
            os.remove(hand_pic)

            await interaction.response.send_message("You can't spectate a game you're playing.", ephemeral=True)
        else:
            try:
                #Delete old ephemeral message and create new one (will fault if no previous message)
                index = spectators.index(interaction.user)
                await spectator_messages[index].delete_original_response()
                spectator_messages[spectators.index(interaction.user)] = interaction

            except ValueError as e:
                #This stops the error from printing to the terminal for firt-time spectators
                pass

            finally:
                spectators.append(interaction.user)
                spectator_messages.append(interaction)
                await interaction.response.send_message(content=player_text, file=discord.File(hand_pic), ephemeral=True)

                #Free discord.File variable so that card art can be deleted
                os.remove(game.get_path(hand_pic))

    #Shows player's thrown cards
    @tree.command(name="thrown", description='''See the cards you've thrown.''')
    async def thrown(interaction):
        #If player not in game, will fail
        try:
            player_index = game.players.index(interaction.user)
            card_string = "Thrown cards: "

            for card in game.thrown_cards[player_index]:
                card_string += card.display() + ", "
            
            await interaction.response.send_message(content=card_string[0:-2], ephemeral=True)
        except:
            await interaction.response.send_message(content="You must be in the game to see the thrown cards.", ephemeral=True)

    #Sends each available command
    @tree.command(name="help", description='''See all available commands.''')
    async def help_command(interaction):
        await interaction.response.send_message(message.help_message(), ephemeral=True)

    @client.event
    async def on_message(msg):
        if msg.author == client.user:
            return
        
        await message.process_message(msg)

        #If spectators, update hands
        if len(spectators) > 0:
            hand_pic = await game.get_all_hand_pics()
            player_text = ""
            for player in game.players:
                player_text += player.name + ", "
            player_text = player_text[:-2] #Remove ", " from end

            for spectator_message in spectator_messages:
                await spectator_message.edit_original_response(content=player_text, attachments=[discord.File(hand_pic)])

            #Free discord.File variable so that card art can be deleted
            os.remove(hand_pic)

    #On startup, sync command tree
    @client.event
    async def on_ready():
        await tree.sync()
        print("Cribbage Bot is ready!")

    # Try to run the bot
    try:
        client.run(discord_token)
    except Exception as e:
        print(format.error(str(e)))
        exit(1)