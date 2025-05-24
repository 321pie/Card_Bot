from bs4 import BeautifulSoup as soup
from datetime import datetime
import re
import requests
import os
from typing import Callable

class General:
    link = "https://docs.google.com/spreadsheets/d/1zUblRLIugMxcqi-2R0AiEAx7gt9FnujT5ik7JB0viaw/edit?gid=2086363072#gid=2086363072"
    file = "src/Stats/general_stats.txt"
    username = "Username"
    total_wins = "Total Wins"
    total_losses = "Total Losses"
    unique_days_played = "Unique Days Played"
    last_date_played = "Last Date Played"
    times_becoming_gm = "Times Becoming GM"
    times_becoming_db = "Times Becoming DB"
    times_becoming_gg = "Times Becoming GG"
    times_becoming_tl = "Times Becoming TL"

class Cribbage:
    link = "https://docs.google.com/spreadsheets/d/1zUblRLIugMxcqi-2R0AiEAx7gt9FnujT5ik7JB0viaw/edit?gid=0#gid=0"
    file = "src/Stats/cribbage_stats.txt"
    username = "Username"
    total_wins = "Total Cribbage Wins"
    total_losses = "Total Cribbage Losses"
    total_skunks = "Total Skunks"
    total_double_skunks = "Total Double+ Skunks"
    total_times_skunked = "Total Times Skunked"
    total_times_double_skunked = "Total Times Double+ Skunked"
    standard_wins = "Standard Wins"
    standard_losses = "Standard Losses"
    standard_joker_wins = "Standard Joker Wins"
    standard_joker_losses = "Standard Joker Losses"
    reverse_standard_wins = "Reverse Standard Wins"
    reverse_standard_losses = "Reverse Standard Losses"
    reverse_standard_joker_wins = "Reverse Standard Joker Wins"
    reverse_standard_joker_losses = "Reverse Standard Joker Losses"
    standard_mega_wins = "Standard Mega Wins"
    standard_mega_losses = "Standard Mega Losses"
    joker_mega_wins = "Joker Mega Wins"
    joker_mega_losses = "Joker Mega Losses"
    reverse_standard_mega_wins = "Reverse Standard Mega Wins"
    reverse_standard_mega_losses = "Reverse Standard Mega Losses"
    reverse_joker_mega_wins = "Reverse Joker Mega Wins"
    reverse_joker_mega_losses = "Reverse Joker Mega Losses"
    times_changing_hand_joker = "Times Changing Hand Joker"
    times_changing_flipped_joker = "Times Changing Flipped Joker"
    times_changing_crib_joker = "Times Changing Crib Joker"
    highest_standard_hand = "Highest Standard Hand"
    highest_standard_joker_hand = "Highest Standard Joker Hand"
    highest_reverse_standard_joker_hand = "Highest Reverse Standard Joker Hand"
    highest_reverse_standard_hand = "Highest Reverse Standard Hand"
    highest_standard_mega_hand = "Highest Standard Mega Hand"
    highest_joker_mega_hand = "Highest Joker Mega Hand"
    highest_reverse_standard_mega_hand = "Highest Reverse Standard Mega Hand"
    highest_reverse_joker_mega_hand = "Highest Reverse Joker Mega Hand"
    lowest_standard_hand = "Lowest Standard Hand"
    lowest_standard_joker_hand = "Lowest Standard Joker Hand"
    lowest_reverse_standard_joker_hand = "Lowest Reverse Standard Joker Hand"
    lowest_reverse_standard_hand = "Lowest Reverse Standard Hand"
    lowest_standard_mega_hand = "Lowest Standard Mega Hand"
    lowest_joker_mega_hand = "Lowest Joker Mega Hand"
    lowest_reverse_standard_mega_hand = "Lowest Reverse Standard Mega Hand"
    lowest_reverse_joker_mega_hand = "Lowest Reverse Joker Mega Hand"
    total_points_scored = "Total Points Scored"

achievement_categories = [General, Cribbage]

#Loads pages from remote, compares to local, and saves newest version to local (must be written to remote manually as of now)
def load_pages():
    for achievement_category in achievement_categories:
        page = requests.get(achievement_category.link)

        html = soup(page.content, "html.parser")

        remote_page_data = []
        rows = html.find_all("tr")
        for row in rows:
            items = row.find_all("td")
            row_data = [item.text for item in items]
            
            #If row is empty, then abort (all valid rows have been checked)
            if len(row_data) > 0:
                if all(item == "" for item in row_data):
                    #Save local data to variable and get dates of both
                    local_page_data = read_from_file(achievement_category)
                    if local_page_data != None:
                        local_date = access_last_updated_date(local_page_data)
                        remote_date = access_last_updated_date(remote_page_data)

                        #If local is more recently updated than remote, combine with remote data in case new columns were added
                        if remote_date < local_date:
                            #TODO: Combine
                            print("Combining, but not really ;p")
                            remote_page_data = local_page_data #Wow, very elegant, AMAZING even
                        
                    write_to_file(achievement_category, remote_page_data)

                    break
                else:
                    remote_page_data.append(row_data)

#Updates/fetches a field on local. Can pass in data, or if data is None, the data will be overwritten by passing in the current value to func and writing the return value. If both data and func are None, then return the data without changing it.
#Returns true on succesful update, the value of the field on sucessful fetch, and None if an error occurs
def access_field(achievement_category, user:str, field_name:str, data:str=None, func:Callable[[str], str]=None) -> any:
    #Get relevent data
    page_data = read_from_file(achievement_category)

    #Get index of user
    try:
        username_index = page_data[0].index("Username")
    except:
        #print('''"Username" header not found on page''')
        return None
    
    user_index = None
    if len(page_data) > 2:
        for row_index in range(len(page_data[2:])): #Since we're skipping the header and default player row, add 2 to index in future
            if page_data[row_index+2][username_index] == user:
                user_index = row_index+2
                break

    if user_index == None:
        #print("User not found")
        return None

    #Get index of field to update
    try:
        header_index = page_data[0].index(field_name)
    except:
        #print("Field name not found")
        return None
    
    #Update or return field
    if data == None and func == None:
        return page_data[user_index][header_index]
    elif data != None:
        page_data[user_index][header_index] = data
    else:
        page_data[user_index][header_index] = func(page_data[user_index][header_index])

    if write_to_file(achievement_category, page_data) == True:
        return True
    else:
        return None
    
#Returns the "last updated" datetime from the specified page (when passed in), and updates the date if do_date_update is true
def access_last_updated_date(page_data:list[list[str]], do_date_update:bool=False) -> datetime:
    saved_date = datetime(*[int(value) for value in re.split('[- :]', page_data[0][page_data[0].index('')-1])])

    if do_date_update == True:
        page_data[0][page_data[0].index('')-1] = str(datetime.today().replace(microsecond=0))

    return saved_date

#Writes a page to the specified file. Returns true on success, else false
def write_to_file(achievement_category, page_data:list[list[str]]) -> bool:
    #Update last updated date
    access_last_updated_date(page_data, True)

    #Edit data for copy/pasting
    data_to_write = ""
    for data in page_data:
        try: #If data isn't a string, then print exception and return false
            data_to_write += '\t'.join(data) + '\n'
        except Exception as e:
            print(e)
            return False
            
    #Write data to file
    with open(achievement_category.file, 'w') as file:
        file.write(data_to_write)

    return True

#Returns the list from the specified file
def read_from_file(achievement_category) -> list[list[str]]:
    #If file doesn't exist, create it
    if not os.path.exists(achievement_category.file):
        with open(achievement_category.file, 'w') as file:
            return None

    #If file exists (always does ;)), then read data from it if possible
    with open(achievement_category.file, 'r') as file:
        page_data = file.read().split('\n')
        page_data = [row.split('\t') for row in page_data[:-1]] #[:-1] to account for the extra \n at the end

    return page_data

#Checks if a player exists. Adds them if they don't. Returns true if they already exist or are created successfully, else false.
def add_player(user:str) -> bool:
    for achievement_category in achievement_categories:
        #If they don't exist, get data, append default user as new entry, and update username to user's username
        if access_field(achievement_category, user, "Username") == None:
            page_data = read_from_file(achievement_category)
            page_data.append(page_data[1])

            if write_to_file(achievement_category, page_data) == False:
                return False
            if access_field(achievement_category, "Default", "Username", user) == False:
                return False
    
    return True

#Adds 1 to a number passed in as a string (for recording things like total wins, total losses, games played, etc.)
def increment(str_num:str):
    return str(int(str_num) + 1)