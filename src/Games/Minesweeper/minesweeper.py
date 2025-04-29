import random

HIDDEN_CHARACTERS = ["||:zero:||", "||:one:||", "||:two:||", "||:three:||", "||:four:||", "||:five:||", "||:six:||", "||:seven:||", "||:eight:||", "||:bomb:||"] #Holds max_bombs number of numbers (in order 0-8) and a bomb character (in that order)
REVEALED_CHARACTERS = [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":bomb:"] #Holds max_bombs number of numbers (in order 0-8) and a bomb character (in that order)
MAX_BOMBS = 10 #Max number of bombs (corresponding index in characters array)

def init_minesweeper(grid_width=5, grid_height=5, num_bombs=3):
    #Make sure ints are passed in
    try:
        grid_width = int(grid_width)
        grid_height = int(grid_height)
        num_bombs = int(num_bombs)
    except:
        return "Invalid parameters. Please enter integers or nothing at all."

    #Set grid to valid values
    if not ((0 < grid_width < 10) and (0 < grid_height < 10)):
        grid_width, grid_height = 5

    grid_width = grid_width
    grid_height = grid_height

    #Set up bombs
    if num_bombs < 0:
        num_bombs = 1
    elif num_bombs > MAX_BOMBS:
        num_bombs = MAX_BOMBS

    if num_bombs >= grid_width*grid_height:
        num_bombs = 1

    #populate empty grid with unique numbers
    grid = []
    for grid_square in range(grid_width * grid_height):
        grid.append(grid_square)

    #Get bomb placement and add bombs to grid
    bomb_list = random.sample(grid, num_bombs)
    for bomb in bomb_list:
        grid[grid.index(bomb)] = HIDDEN_CHARACTERS[-1]

    #Populate grid with valid number of bombs from characters
    for square_index in range(len(grid)):
        #Reset number of close bombs and indexes to check
        close_bombs = 0
        check_indexes = [square_index - grid_width, square_index + grid_width]
        if square_index % grid_width != 0:
            check_indexes += [square_index - grid_width - 1, square_index - 1, square_index + grid_width - 1]
        if square_index % grid_width != grid_width-1:
            check_indexes += [square_index - grid_width + 1, square_index + 1, square_index + grid_width + 1]
        
        #If bomb, move on to next. Else, increment bomb count for bombs around you then replace with correct symbol
        if grid[square_index] == HIDDEN_CHARACTERS[-1]:
            continue
        else:
            for index in check_indexes:
                if index>=0 and index<len(grid):
                    if grid[index] == HIDDEN_CHARACTERS[-1]:
                        close_bombs += 1

        grid[square_index] = HIDDEN_CHARACTERS[close_bombs]

    #Returns a string containing a readable grid with a 0 revealed
    return get_grid(reveal_0(grid), grid_width, grid_height, num_bombs)

#Reveals a 0 (if possible, else reveal next lowst numeber)
def reveal_0(grid) -> list[str]:
    loop_done = False
    for index in range(len(HIDDEN_CHARACTERS) - 1): #Iterate through for all numbers (starting with 0's)
        start_index = random.randint(0, len(grid)-1) #Random starting index
        for _ in range(len(grid)): #Iterate through grid backwards from random start_index (since negative wraps)
            if grid[start_index] != HIDDEN_CHARACTERS[index]: #If wrong, keep going
                start_index -= 1
            else: #If right, change to revealed, signal loop is done, and break
                grid[start_index] = REVEALED_CHARACTERS[index]
                loop_done = True
                break

        if loop_done: #If loop is doen, break. Else, move on to next number
            break

    return grid

#Puts the grid into a readable format
def get_grid(grid, grid_width, grid_height, num_bombs) -> str:
    output_str = ""

    for row in range(grid_height):
        output_str += "\n"
        for column in range(grid_width):
            output_str += str(grid[row*grid_width + column]) + " "

    if num_bombs == 1:
        return output_str + f"\nThere is {num_bombs} bomb. Have fun!"
    else:
        return output_str + f"\nThere are {num_bombs} bombs. Have fun!"