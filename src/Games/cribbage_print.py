from Backend.cribbage import Cribbage
from game_print import game_print

class cribbage_print(game_print):
    def __init__(self):
        super.__init__()
        self.game = Cribbage()
        self.commands["^![0-9]+$"] = [self.select_card, self.select_card_parse]

    #Input: parse string of form "^![0-9]+$"
    #Output: integer index parsed from string
    def select_card_parse(self, parse_str):
        return int(parse_str[1:])

    #Input: integer index parsed from string
    #Output: list of return statements using add_return
    def select_card(self, player, index):
        if(player in self.game.players):
            #Check for valid index or return
            if(index >= len(self.game.hands[self.game.players.index(player)]) or index < 0):
                return []

            if(self.game.game_started == True):
                if(self.game.throw_away_phase == True):
                    return self.throw_away_phase_func(player, index)
                elif(self.game.pegging_phase == True):
                    return self.pegging_phase_func(player, index)

        return []

    async def throw_away_phase_func(self, author, card_index):
        return_list = []

        #Don't do anything if player not in game.
        if(author not in self.game.players):
            return return_list
        
        #If player has joker card (joker mode), force them to make joker something before anybody throws.
        if self.game.check_hand_joker() != None:
            return self.add_return(return_list, f"You can't throw away cards until {self.game.check_hand_joker().name} has chosen which card to turn their joker into.")

        #If throwing away a card fails, alert player.
        if(self.game.throw_away_card(author, card_index) == False):
            return add_return(return_list, f"You have already thrown away the required number of cards, {author.name}.")

        #Update hand if applicable.
        await update_hand(author)

        #Check if everyone is done. If not, return. Else, get flipped card and begin pegging round.
        if(game.is_finished_throwing(author)):
            if(not game.everyone_is_finished_throwing()):
                add_return(return_list, f'''{author.name} has finished putting cards in the crib.''')
                return return_list
            else:
                game.prepare_pegging()

                #Add display text
                flipped = game.deck.get_flipped()
                if(flipped.value != dk.JACK):
                    add_return(return_list, f'''{author.name} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.''')
                else:
                    add_return(return_list, f'''{author.name} has finished putting cards in the crib.\nFlipped card is: {flipped.display()}.\n{game.players[game.crib_index % len(game.players)]} gets nibs for 2.''')
                
                #Check for winner
                if(game.get_winner() != None):
                    return add_return(return_list, game.get_winner_string(game.get_winner()))
                
                #Check for flipped joker
                if(flipped.value == dk.JOKER):
                    add_return(return_list, f"***{game.players[game.crib_index % len(game.players)].name} must choose which card to turn the flipped joker into before game can proceed.***")
                else:
                    add_return(return_list, f"Pegging will now begin with **{game.players[game.pegging_index]}**.")
            
        return return_list