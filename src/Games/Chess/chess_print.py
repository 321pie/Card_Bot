import copy
import io
import itertools
from collections import OrderedDict

from Games.Chess.chess import Chess
from Games.Chess.chess import Piece
from Games.Chess.chess import PieceType
from Games.game_print import Game_Print

class Chess_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        super().__init__()
        self.game = Chess()
        self.commands["![a-z]1?[0-9][a-z]1?[0-9]$"] = [self.move, self.get_move]
        self.commands["!teams$"] = [self.set_teams]

    def get_move(self, move):
        return [move]

    async def move(self, player, pos):
        if(self.game.players.index(player) == self.game.current_turn):
            msg = self.game.move(pos)
            return self.add_return([], msg)
    
    async def set_teams(self):
        return self.add_return([], "Teams have not been implimented.")
    
    #Returns current chess board as a string
    def print_board(self) -> str:
        output = "\n```"
        if len(self.game.players) == 2:
            output += "┌－┬－┬－┬－┬－┬－┬－┬－┐\n"
            for row in self.game.board:
                for piece in row:
                    match piece.type:                    
                        case PieceType.INVALID:
                            output += " 　"
                        case PieceType.EMPTY:
                            output += "│　"
                        case PieceType.PAWN:
                            if piece.player == 0:
                                output += "│♟"
                            else:
                                output += "│♙"
                        case PieceType.KNIGHT:
                            if piece.player == 0:
                                output += "│♞"
                            else:
                                output += "│♘"
                        case PieceType.BISHOP:
                            if piece.player == 0:
                                output += "│♝"
                            else:
                                output += "│♗"
                        case PieceType.ROOK:
                            if piece.player == 0:
                                output += "│♜"
                            else:
                                output += "│♖"
                        case PieceType.QUEEN:
                            if piece.player == 0:
                                output += "│♛"
                            else:
                                output += "│♕"
                        case PieceType.KING:
                            if piece.player == 0:
                                output += "│♚"
                            else:
                                output += "│♔"
                output += "│\n├－┼－┼－┼－┼－┼－┼－┼－┤\n"
            output = output[:-18]
            output += "└－┴－┴－┴－┴－┴－┴－┴－┘"
        else:
            output += "Whoops! Something went wrong!"
        output += "```"
        return output

    #Returns the string to be displayed when the game is started
    def get_start_string(self, player) -> str:
        output = "Chess has begun!"
        output += self.print_board()
        output += "\n" + self.game.players[0] + " is going first!"
        return output
    
    #Returns the string to be displayed when the game is ended
    def get_end_string(self, player) -> str:
        return "Checkmate! " + self.game.winner + " has won the game!"