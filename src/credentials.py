###########################################################
# File: credentials.py
#
# Authors: Bryce Schultz
# Date: 4/10/2024
#
# Description: This file contains a 
# function that loads the discord token from a file.
###########################################################

# Foreign imports
import json

# Local imports
import format

###########################################################
# Function: load_from_file
#
# Loads the discord token from the credentials file safely.
# If the file doesn't exist, the user will be prompted to create it.
#
# Returns the discord token if successful, otherwise None.
#
def load_from_file(file: str) -> str:
    # Try to open the credentials file. 
    # If it doesn't exist, ask the user if they want to create it.
    try:
        credentials_file = open(file, 'r')
    except FileNotFoundError:
        # Ask the user if they want to create the file.
        should_create_file = input(
            format.warning(f'{file} not found. Would you like to create it? (y/n): '))

        # If the user doesn't want to create the file, exit.
        if should_create_file != 'y':
            return None
        
        # Get the token from the user.
        token = input("Enter bot token: ")

        # Open the file and write the token.
        credentials_file = open(file, 'w')
        credentials_file.write('{ "token": "' + token + '" }')
        credentials_file.close()

        # Reopen the file for reading.
        credentials_file = open(file, 'r')
    except Exception as e:
        print(format.error(str(e)))
        return None
    
    # Try to load the token from the file, and catch any exceptions.
    try:
        # Load the token from the file.
        discord_token = json.load(credentials_file)['token']
    except json.JSONDecodeError:
        print(format.error(f'{file} is not formatted correctly.'))
        return None
    except KeyError:
        print(format.error(f'{file} is missing the token field.'))
        return None
    except Exception as e:
        print(format.error(str(e)))
        return None
    
    # Close the file and return the token.
    credentials_file.close()
    return discord_token