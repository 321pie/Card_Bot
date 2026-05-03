# Card Bot

This project is a rework of the [old cribbage bot](https://github.com/AbbeyRDuBois/Cribbage_Counter).<br>
You can find the cribbage calculator GUI from that project as an exe file under src/Games/Cribbage.

Card Bot allows for multiple games to be added, and will likely grow with time.

For the optimal playing experience, listen to the [official cribbage playlist](https://open.spotify.com/playlist/62dcOrotfvGu6k6UzyuDIg?si=e9c16a562cb8407a)!

[Non-Programmer Friendly Instructions](https://docs.google.com/document/d/1ZA37ccEDgdsJG2t4bXch4cNlkp_BOfKMuwSogXjJ1p8/edit?usp=sharing)

<details>
<summary>Table of Contents (Click Here)</summary>

[Requirements](#requirements)

[Setup](#setup) <br/>
&nbsp;&nbsp; [Running the Program](#running) <br/>
&nbsp;&nbsp; [Alternate Setup](#asetup)

[Creating Bot, Getting Token, and Inviting to Server](#botsetup)

[Code Introduction](#orientation)

</details>

## <a id="requirements"/> Requirements:
* python 3
* pip 3

## <a id="setup"/> Setup:

Start by installing the dependencies using the setup script:

linux:
```bash
./setup
```

windows:
```cmd
./setup.bat
```

### <a id="running"/> Running the Program:
Launch the bot using the start script:

linux:
```bash
./start
```

windows:
```cmd
./start.bat
```

When opening the program for the first time you will be asked if you want to create the credentials.json file.
The file will be created in the current working directory so be sure you are in the root project folder when you run this.

Enter `y` and the file will be created.

You will then be prompted to enter your discord bot token.
Enter the token and the bot will try to launch.

If you want to stop the bot, hit Ctrl+C in the terminal and you will be prompted to stop the bot.

Note: Bots must be invited to a Discord server in order to be used. More on how to create a bot, get the token, and invite the bot to a server below.

### <a id="asetup"/> Alternate Setup:
If you would like to enter the token manually, create a file called credentials.json in the root folder of the project and enter the following:

```json
{ "token": "YOUR_API_KEY_HERE" }
```

Replace YOUR_API_TOKEN_HERE with your discord bot's token.

## <a id="botsetup"/> Creating Bot, Getting Token, and Inviting to Server:
[Link to create a bot](https://discord.com/developers/applications)

1) Select the "Applications" tab on the left and click the "New Application" button in the top right.

2) Name the bot, accept the terms of service, and hit "Create".

3) Go to the "Bot" tab and hit the slider to enable Message Content Intent.

4) Go to the "OAuth2" tab, and select "bot" in the OAuth2 URL Generator section.

5) In the Bot Permissions section, select the following (not all are used in current version of Cribbage Bot):

    * Manage Roles
    * Send Messages
    * Create Public Threads
    * Create Private Threads
    * Send Messages in Threads
    * Manage Messages
    * Manage Threads
    * Embed Links
    * Attach Files
    * Read Mesage History
    * Mention Everyone
    * Add Reactions
    * Use Slash Commands
    * Use Embedded Activities (x2)

6) Use the generated url at the bottom of the page to invite the bot to a server you have administrator access to.

7) You can get your token/client secret from the same tab (the "OAuth2" tab), which is needed to run the bot and can be used as outlined above.
If you don't have it or accidentally share it, click "Reset Secret" to get another (old tokens won't work, so be sure to update credentials.json accordingly).

## <a id="orientation"> Code Introduction:

This codebase uses a Model View Controller (<a href="https://www.geeksforgeeks.org/mvc-framework-introduction/">MVC</a>) architecture.

The model (business logic) is kept in a class that inherits from game.py (see juiced.py for an example).

The controller (UI logic) is kept in a class that inherits from game_print.py (see juiced_print.py for an example).

The view (input logic) is primarily kept in message.py (! commands), though some is also located in bot.py (/ commands).

Check out game.py, game_print.py, and message.py before trying to add to the codebase. These files hold the basic building blocks for any game.<br/>
If you want to add a game, then create a new branch for the game and submit a pull request when the game is completed.<br/>
Testing can be done using the testing feature (more information on the test feature can be found by using /help or reading help.txt).<br/>
If you want to add stats/achievements, ask for permissions to edit the <a href="https://docs.google.com/spreadsheets/d/1zUblRLIugMxcqi-2R0AiEAx7gt9FnujT5ik7JB0viaw/edit?usp=sharing">Google Sheets document</a> and then add your achievements to the controller as well as stats.py.



