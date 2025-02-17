from bs4 import BeautifulSoup as soup
import requests
from typing import Callable

GENERAL = ("https://docs.google.com/spreadsheets/d/1zUblRLIugMxcqi-2R0AiEAx7gt9FnujT5ik7JB0viaw/edit?gid=2086363072#gid=2086363072", "stats/general_stats.txt")
CRIBBAGE = ("https://docs.google.com/spreadsheets/d/1zUblRLIugMxcqi-2R0AiEAx7gt9FnujT5ik7JB0viaw/edit?gid=0#gid=0", "stats/cribbage_stats.txt")

LINK_INDEX = 0
FILE_INDEX = 1

ACHIEVEMENTS = [GENERAL, CRIBBAGE]

#Loads pages from remote, compares to local, and saves newest version to local (must be written to remote manually as of now)
def get_pages():
    pages = []
    for achievement_tuple in ACHIEVEMENTS:
        page = requests.get(achievement_tuple[LINK_INDEX])

        html = soup(page.content, "html.parser")

        page_data = []
        rows = html.find_all("tr")
        for row in rows:
            items = row.find_all("td")
            row_data = [item.text for item in items]
            
            #If row is empty, then abort (all valid rows have been checked)
            if len(row_data) > 0:
                if all(item == "" for item in row_data):
                    #TODO: Compare local to remote, save old first in case new columns were added, then save new over the top
                    #Update file and write to return variable before moving to next page
                    if write_to_file(achievement_tuple, page_data) == True:
                        pages.append(page_data)
                    break
                else:
                    page_data.append(row_data)

    return pages

#Updates a field on local. Can pass in data, or if data is None, the data will be overwritten by passing in the current value to func and writing the return value. Returns true on succesful update, else false
def update_field(achievement_tuple:tuple, user:str, field_name:str, data:str=None, func:Callable[[str], str]=None) -> bool:
    #If no data to update, then update failed
    if data == None and func == None:
        return False
    
    with open(achievement_tuple[FILE_INDEX], 'r') as file:
        page_data = file.read().split('\n')
        page_data = [row.split('\t') for row in page_data[:-1]] #[:-1] to account for the extra \n at the end

    #Get index of user
    try:
        username_index = page_data[0].index("Username")
    except:
        print('''"Username" header not found on page''')
        return False
    
    user_index = None
    for row_index in range(len(page_data[1:])): #Since we're skipping the header row, add 1 to index in future
        if page_data[row_index+1][username_index] == user:
            user_index = row_index+1
            break

    if user_index == None:
        print("User not found")
        return False

    #Get index of field to update
    try:
        header_index = page_data[0].index(field_name)
    except:
        print("Field name not found")
        return False
    
    #Update field
    if data != None:
        page_data[user_index][header_index] = data
    else:
        page_data[user_index][header_index] = func(page_data[user_index][header_index])

    if write_to_file(achievement_tuple, page_data) == True:
        return True
    else:
        return False

#Writes a page to the specified file. Returns true on success, else false
def write_to_file(achievement_tuple:tuple, page_data:list[list[str]]) -> bool:
    data_to_write = ""
    for data in page_data:
        try: #If data isn't a string, then print exception and return false
            data_to_write += '\t'.join(data) + '\n'
        except Exception as e:
            print(e)
            return False
            
    with open(achievement_tuple[FILE_INDEX], 'w') as file:
        file.write(data_to_write)
            
    return True

#Adds 1 to a number passed in as a string (for recording things like total wins, total losses, games played, etc.)
def increment(str_num:str):
    return str(int(str_num) + 1)