import copy
import io
import itertools
from collections import OrderedDict

from Games.Chess.chess import Chess
from Games.game_print import Game_Print

class Chess_Print(Game_Print):
    HAND_PIC = False

    def __init__(self):
        super().__init__()
        self.game = Chess()
        self.commands["![a-z]1?[0-9][a-z]1?[0-9]$"] = [self.move, self.parse_pos]
        self.commands["!teams$"] = [self.set_teams]

    async def move(self, player, pos_a:str, pos_b:str):
        return self.add_return([], self.game.move(player, pos_a, pos_b))
    
    def parse_pos(self, parse_str) -> list[str]:
        return parse_str.split(" ")
    
    async def set_teams(self):
        return self.add_return([], "Teams have not been implimented.")