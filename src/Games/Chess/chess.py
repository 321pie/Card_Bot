from enum import Enum
import re

import Games.game as game

class Chess(game.Game):
    def __init__(self):
        super().__init__()
        self.req_players:int = 2
        self.current_turn:int = 0
        self.board:list = []
        self.winner:str = "Nobody"

    def initialize_game(self) -> bool:
        match len(self.players):
            case _ if len(self.players) < self.req_players:
                return False
            case _ if len(self.players) > 4:
                return False
            case 3:
                return False
            case 2:
                self.board.append([Piece(1, PieceType.ROOK),   Piece(1, PieceType.KNIGHT), Piece(1, PieceType.BISHOP), Piece(1, PieceType.QUEEN),  Piece(1, PieceType.KING),   Piece(1, PieceType.BISHOP), Piece(1, PieceType.KNIGHT), Piece(1, PieceType.ROOK)])
                self.board.append([Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN),   Piece(1, PieceType.PAWN)])
                self.board.append([Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY)])
                self.board.append([Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY)])
                self.board.append([Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY)])
                self.board.append([Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY), Piece(-1, PieceType.EMPTY)])
                self.board.append([Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN),   Piece(0, PieceType.PAWN)])
                self.board.append([Piece(0, PieceType.ROOK),   Piece(0, PieceType.KNIGHT), Piece(0, PieceType.BISHOP), Piece(0, PieceType.QUEEN),  Piece(0, PieceType.KING),   Piece(0, PieceType.BISHOP), Piece(0, PieceType.KNIGHT), Piece(0, PieceType.ROOK)])
            case 4:
                #TODO: 4 player board initialization
                return False
            
        #print board
        #TODO

    def move(self, pos) -> str:
        parts = re.split(r'(\d+)', pos[1:])
        start_x = ord(parts[0][0]) - 96
        start_y = int(parts[1])
        end_x = ord(parts[2][0]) - 96
        end_y = int(parts[3])
        piece = self.board[start_y][start_x]

        if start_x < 0 or start_x > len(self.board) or start_y < 0 or start_y > len(self.board):
            return "Selected space not on the board"
        if end_x < 0 or end_x > len(self.board) or end_y < 0 or end_y > len(self.board):
            return "Target space not on the board"

        if piece.player == -1:
            return "Selected space does not contain a piece."
        elif piece.player != self.current_turn:
            return "Selected piece is not yours."
        
        match piece.type:
            case PieceType.PAWN:
                return "Pawn"
            case PieceType.KNIGHT:
                return "Knight"
            case PieceType.BISHOP:
                return "Bishop"
            case PieceType.ROOK:
                return "Rook"
            case PieceType.QUEEN:
                return "Queen"
            case PieceType.KING:
                return "King"

        #remove old piece
        piece.player = -1
        piece.type = PieceType.EMPTY

        #pass the turn
        self.current_turn += 1
        self.current_turn = self.current_turn % len(self.players)

        #print board
        #TODO

        #check for win

class PieceType(Enum):
    INVALID = -1
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Piece():
    def __init__(self, player, type):
        self.player:int = player
        self.type:PieceType = type

