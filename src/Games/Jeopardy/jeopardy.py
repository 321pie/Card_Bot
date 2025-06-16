from copy import copy
from random import randint, sample
from re import findall

from Games.game import Game
import Games.Jeopardy.questions as qs

class Jeopardy(Game):
    #Inits variables common to all games
    def __init__(self):
        super().__init__()
        self.min_player_count:int = 1 #Defines the minimum number of players that have to !join before the game can start
        self.max_player_count:int = 8 #Defines the maximum number of players
        self.play_index:int = 0 #Index of the selecting player
        self.categories:list[str] = [] #List of all of the categories on board, indexed accordingly (categories[0] -> board[0])
        self.board:list[list[tuple]] = [] #Contains all of the questions and answers in tuples
        self.daily_double_indexes:list[tuple] = [] #Tuple with the index of the daily double (column, row)
        self.rows = 6 #Number of rows on board
        self.columns = 6 #Number of columns on board
        self.questions:dict = copy(qs.STD_QUOTES) #Dictionary with category as key and list of quotes as the value
        self.points:list[int] = [] #List to hold point totals (indexed same as players)
        self.show_word_length = False #Decides if missing word length is reflected by underscores provided.
        self.increase_amount = 200 #Amount of points that each question increases by.
        self.players_passing:list = [] #List that holds the names of the players that have agreed to pass the round.
        self.question_index:tuple = None #Holds he index of the current question (column, row)
        self.wager_amount:int = None #Amount wagered in daily double

    #Initializes the game on start
    #Returns True on success, False on failure
    def initialize_game(self) -> bool:
        #Init variables to initialize the game
        for _ in self.players:
            self.points.append(0)
            self.players_passing.append(None)

        #Check to make sure that there are enough items in the dict
#TODO: Check that there are enough items in dict that have self.rows number of items.
        if len(self.questions) < self.columns:
            self.columns = 6
            self.rows = 6
        
        questions = sample(list(self.questions.items()), self.columns)
        
        #Create board
        for my_tuple in questions:
            key, value = my_tuple

            #Get the random questions from the categories
            row_questions = sample(value, self.rows)

            #Create (quote, answer) pairs.
            for quote_index in range(len(row_questions)):
                answer = sample(findall('''[a-zA-Z]+''', row_questions[quote_index]), 1)[0]
                replacement = "_" * len(answer) if self.show_word_length else "___"
                print(answer)
                row_questions[quote_index] = (row_questions[quote_index].replace(answer, replacement, 1), answer.lower())

            #Append column to board
            self.board.append([key] + row_questions)
        
        #Create a daily double square
        self.daily_double_indexes = (randint(0, self.columns-1), randint(1, self.rows-1)) #-1 since 0 indexed and start at 1 on row due to headers
    
    #Takes in the player and their guess and returns the change in points
    def guess(self, player, guess:str) -> int:
        #Check that question has been selected
        if self.question_index == None:
            return 0
        
        #lowercase guess
        guess = guess.lower()
        
        #If daily double, wager amount has been set, and player is correct, check answer and reset.
        if self.is_daily_double():
            if self.wager_amount != None:
                if self.players.index(player) == self.play_index:
                    answer = self.board[self.question_index[0]][self.question_index[1]][1]
                    if guess == answer:
                        self.points[self.play_index] += self.wager
                        self.reset_round()
                        return self.wager
                    else:
                        self.points[self.play_index] -= self.wager
                        self.reset_round()
                        return self.wager * -1
        #If not daily double, check answer. Reset round if correct.
        else: 
            player_index = self.players.index(player)
            answer = self.board[self.question_index[0]][self.question_index[1]][1]
            points = self.question_index[1] * self.increase_amount
            if guess == answer:
                self.points[player_index] += points
                self.play_index = player_index
                self.reset_round()
                return points
            else:
                self.points[player_index] -= points
                return points * -1


    #Takes in the player who is passing the round. Returns True if all players have passed the round, else False
    def pass_round(self, player):
        #Add player to players_passing
        player_index = self.players.index(player)
        self.players_passing[player_index] = player

        #Return false if any players are None (default value) unless it's daily double (only one person can answer)
        if player_index != self.play_index or not self.is_daily_double():
            for name in self.players_passing:
                if name == None:
                    return False
            
        #Reset round and return that round has been reset
        self.reset_round()
        return True
    
    #Resets variables when round ends
    def reset_round(self):
        #Reset players who passed the round
        self.players_passing = []
        for _ in self.players:
            self.players_passing.append(None)

        #Remove question by setting to None
        self.board[self.question_index[0]][self.question_index[1]] = (None, None)

        #Check if game is over
        broken = False
        for column in self.board:
            for row_tuple in column:
                if row_tuple[0] != None:
                    broken = True
                    break
            if broken:
                break
        
        #If not broken, end game
        if not broken:
            self.end_game()

        #Reset other variables to base value (None)
        self.question_index = None
        self.wager_amount = None

    #If the wager was set, return True. Else, return False.
    def wager(self, player, amount):
        if self.is_daily_double():
            if self.wager_amount == None:
                if self.players.index(player) == self.play_index:
                    if 0 <= amount <= self.game.get_increase_amount() * self.game.get_row_count() * 2:
                        self.wager_amount = amount

                        return True
                    
        return False

    #If selected question was valid, return question. Else, return None.
    def select_question(self, player, row:int, column:int):
        if self.question_index == None:
            if player == self.get_play_player():
                if 0 < row < self.rows and 0 <= column < self.columns:
                    if self.board[column][row][0] != None:
                        self.question_index = (column, row)
                        return self.board[column][row][0]
        
        return None
    
    #Gets the player who selects the question
    def get_play_player(self):
        return self.players[self.play_index]
    
    #Returns the question, or None if no question is available
    def get_question(self):
        if self.question_index != None:
            return self.board[self.question_index[0]][self.question_index[1]][0]
        else:
            return None

    #Returns the current question's answer, or None if no question is available
    def get_answer(self):
        if self.question_index != None:
            return self.board[self.question_index[0]][self.question_index[1]][1]
        else:
            return None
        
    #Return a list of (player, points) tuples
    def get_points(self):
        return_list = []
        for player_index in range(len(self.players)):
            return_list.append((self.players[player_index], self.points[player_index]))

        return return_list
        
    #Gets the point value of the current question, or None if no question
    def get_value(self):
        if self.question_index != None:
            return self.question_index[1] * self.increase_amount
        else:
            return None
        
    #Returns the board as a list of lists as the player would see it (each list is a category followed by the point values or None if answered already)
    def get_board(self):
        # board = []

        # for column in self.board:
        #     col = []
        #     for question_index in range(len(column)):
        #         if question_index == 0:
        #             col.append(column[question_index])
        #         elif column[question_index] == None:
        #             col.append(None)
        #         else:
        #             col.append(question_index * self.increase_amount)

        #     board.append(col)

        return copy(self.board)
    
    #Gets number of columns in board
    def get_column_count(self):
        return self.columns
    
    #Gets number of rows in board
    def get_row_count(self):
        return self.rows
    
    #Gets the current wager, defaults to None
    def get_wager(self):
        return self.wager_amount
    
    #Gets the amount that the score increases by
    def get_increase_amount(self):
        return self.increase_amount
    
    #Returns True if question is in the daily double, else False
    def is_daily_double(self):
        if self.question_index in self.daily_double_indexes:
            return True
        else:
            return False