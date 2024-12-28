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

#Local imports
import message
import credentials

# spectators = []
# spectator_messages = []

#Gets the path for the images
def get_path(limited_path):
    # if(EXECUTABLE_MODE):
    #     return sys.executable.rsplit('\\', 2)[0] + '\\' + limited_path
    # else:
    # return os.path.join(os.path.dirname(__file__), limited_path)
    return os.path.join(os.getcwd(), limited_path)

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
    async def hand_command(interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        player = interaction.user.name

        for active_game in message.active_games:            
            if active_game.HAND_PIC == True:
                if player in active_game.get_players():
                    hand_pic = active_game.get_hand_pic(player) #Get hand pic to display (or None if invalid)
                    await active_game.delete_last_hand(player, interaction) #Delete old ephemeral message and create new one
                    if hand_pic == None:
                        await interaction.followup.send(content="Failed to retrieve hand.", ephemeral=True)
                    else:
                        await interaction.followup.send(content="Use command below card to play it.", file=discord.File(fp=hand_pic, filename="HandPic.png"), ephemeral=True)
                    break
            elif active_game.HAND_PIC == False:
                if player in active_game.get_players():
                    hand_str = active_game.get_hand_string(player) #Get hand pic to display (or None if invalid)
                    await active_game.delete_last_hand(player, interaction) #Delete old ephemeral message and create new one
                    await interaction.followup.send(content=hand_str, ephemeral=True)
                    break

    #Sends the rules of cribbage
    @tree.command(name="rules", description='''See the rules.''')
    async def rules_command(interaction:discord.Interaction):
        await interaction.response.send_message(content="Rules outlined below.", file=discord.File(get_path("src\\rules.txt")), ephemeral=True)

    # #Sends every player's hand if player not in game
    # @tree.command(name="spectate", description='''See every players' hands.''')
    # async def spectate_command(interaction):
    #     global spectators
    #     global spectator_messages
        
    #     player_text = ""
    #     for player in game.players:
    #         player_text += player.name + ", "
    #     player_text = player_text[:-2] #Remove ", " from end
    #     hand_pic = await game.get_all_hand_pics()

    #     if interaction.user in game.players:
    #         #Free discord.File variable so that card art can be deleted
    #         os.remove(hand_pic)

    #         await interaction.response.send_message("You can't spectate a game you're playing.", ephemeral=True)
    #     else:
    #         try:
    #             #Delete old ephemeral message and create new one (will fault if no previous message)
    #             index = spectators.index(interaction.user)
    #             await spectator_messages[index].delete_original_response()
    #             spectator_messages[spectators.index(interaction.user)] = interaction

    #         except ValueError as e:
    #             #This stops the error from printing to the terminal for firt-time spectators
    #             pass

    #         finally:
    #             spectators.append(interaction.user)
    #             spectator_messages.append(interaction)
    #             await interaction.response.send_message(content=player_text, file=discord.File(hand_pic), ephemeral=True)

    #             #Free discord.File variable so that card art can be deleted
    #             os.remove(game.get_path(hand_pic))

    #Sends each available command
    @tree.command(name="help", description='''See all available commands.''')
    async def help_command(interaction:discord.Interaction):
        await interaction.response.send_message("View attached file for list of available commands", file=discord.File("help.txt"), ephemeral=True)

    @client.event
    async def on_message(msg):
        global spectators
        global spectator_messages

        if msg.author == client.user:
            return
        
        await message.process_message(msg)

        # #If spectators, update hands
        # if len(spectators) > 0:
        #     hand_pic = await game.get_all_hand_pics()
        #     player_text = ""
        #     for player in game.players:
        #         player_text += player.name + ", "
        #     player_text = player_text[:-2] #Remove ", " from end

        #     for spectator_message in spectator_messages:
        #         hand_pic = self.deck_look.get_hand_pic([self.game.get_hand(player)])
        #         await self.hand_messages[self.game.get_player_index(player)].edit_original_response(attachments=[discord.File(fp=hand_pic, filename="HandPic.png")])
        #         await spectator_message.edit_original_response(content=player_text, attachments=[discord.File(hand_pic)])

    #On startup, sync command tree
    @client.event
    async def on_ready():
        await tree.sync()
        print("Card Bot is ready!")

    # Try to run the bot
    try:
        client.run(discord_token)
    except Exception as e:
        print(format.error(str(e)))
        exit(1)