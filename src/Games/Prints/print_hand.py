from math import floor
from PIL import Image
import pygame as pg
import os

import Games.deck as deck

class Print_Hand():
    #Gets the path for the images
    def get_path(self, limited_path):
        # if(EXECUTABLE_MODE):
        #     return sys.executable.rsplit('\\', 2)[0] + '\\' + limited_path
        # else:
        # return os.path.join(os.path.dirname(__file__), limited_path)
        return os.path.join(os.getcwd(), limited_path)
    
    #Converts a PIL image to a pygame surface
    def pil_image_to_surface(self, pil_image:Image) -> pg.Surface:
        return pg.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
    
    def surface_to_pil_image(self, surface:pg.Surface) -> Image:
        pil_string_image = pg.image.tobytes(surface, "RGBA", False)
        return Image.frombytes("RGBA", (surface.get_width(), surface.get_height()), pil_string_image)
    
    #Returns an Image of the selected card
    def get_card(self, card:deck.Card, index:int=None) -> Image:
        #Define path to assets
        asset_file_path = self.get_path('card_art\\all_assets.png')

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
    
###############################################################################
# List of common functions that must be implemented
###############################################################################
    #Get single picture with all hands in it
    def get_hand_pic(self, hands:list[list[deck.Card]], show_index=True) -> Image:
        return None