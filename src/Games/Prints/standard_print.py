from math import floor
from PIL import Image
import pygame as pg

import Games.Prints.base_print as bp
import Games.deck as deck

class Standard_Print(bp.Base_Print):
    def __init__(self):
        super().__init__() #Not needed due to overwrites

        #The size of the sprites
        self.base_card_width = 32 #Excess room on sprite sheet before first card
        self.base_card_height = 32 #Excess room on sprite sheet before first card
        self.card_width = 32 #Width of each card
        self.card_height = 48 #Heaight of each card
        self.num_width = 16 #Width of each number (for index)
        self.num_height = 16 #Height of each number (for index)
        self.base_num_width = 9 * self.card_width + self.base_card_width #Excess room on sprite sheet before first number
        self.base_num_height = 4 * self.card_height + self.base_card_height + 8 #Excess room on sprite sheet before first number
        self.sprite_scalar = 3 #Multiplier to zoom by to make hand a good size

    #Returns an Image of the selected card
    def get_card(self, card:deck.Card, index:int=None) -> Image.Image:
        #Define path to assets
        asset_file_path = self.get_path('src\\card_art\\all_assets.png')

        #Get values for card in sprite sheet
        if card.value != deck.JOKER:
            #Get right column
            width_multiplier = 4 * floor((card.to_int_runs()-1) / 3)

            #Get right sub-column based on suit
            if card.suit == deck.DIAMOND:
                width_multiplier += 1
            if card.suit == deck.CLUB:
                width_multiplier += 2
            if card.suit == deck.HEART:
                width_multiplier += 3

            #Get right row
            height_multiplier = (card.to_int_runs()+2) % 3

        #Jokers are in a different place, so get those
        else:
            height_multiplier = 1
            width_multiplier = 16 #Fourth column * 4 cards in each column

            if card.suit == deck.RED:
                width_multiplier += 1

        x_coord = self.card_width * width_multiplier + self.base_card_width
        y_coord = self.card_height * height_multiplier + self.base_card_height

        #Grab card from sprite sheet and save it
        sheet = pg.image.load(asset_file_path)
        card_image = sheet.subsurface((x_coord, y_coord, self.card_width, self.card_height))

        card_image = self.surface_to_pil_image(card_image)

        #Add index (![0-9]) to card
        if index != None:
            index_image = Image.new('RGB', (floor(self.card_width/2), floor(self.card_height/2)), color=(0, 0, 0))

            #Get position from spritesheet (manual for 0 due to maths)
            if index != 0:
                num_width_multiplier = (index+2) % 3
                num_height_multiplier = floor((index-1) / 3)
            else:
                num_width_multiplier = 1
                num_height_multiplier = 3

            x_num_coord = self.num_width * num_width_multiplier + self.base_num_width
            y_num_coord = self.num_height * num_height_multiplier + self.base_num_height

            num_image = sheet.subsurface((x_num_coord, y_num_coord, self.num_width, self.num_height))

            #Paste number at correct position on background and index_image at correct position on card with correct size
            index_image.paste(self.surface_to_pil_image(num_image), (floor(self.card_width*3/16), floor(self.card_height*3/16)))
            card_image.paste(index_image, (floor(self.card_width/4), floor(self.card_height/4)))

        #Return image path
        return card_image