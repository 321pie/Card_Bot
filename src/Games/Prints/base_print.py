from PIL import Image
import pygame as pg
import os

import Games.deck as deck

class Base_Print():
    def __init__(self):
        #The size of the sprites
        #TODO: Define these
        self.card_width = 1 #Width of each card
        self.card_height = 1 #Heaight of each card

        #This one can change as needed
        self.sprite_scalar = 3 #Multiplier to zoom by to make hand a good size

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
    
    #Get single picture with all hands in it
    def get_hand_pic(self, hands:list[list[deck.Card]], show_index=True) -> Image:
        #Stores index number
        hand_index = 0
        max_hand_len = 0

        for hand in hands:
            if len(hand) > max_hand_len:
                max_hand_len = len(hand)

        #Create empty image with place for images
        if max_hand_len == 0:
            max_hand_len == 1
        all_hands_img = Image.new('RGB', (self.card_width*max_hand_len, self.card_height*len(hands)), color=(0, 80, 80))

        #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
        for hand_index in range(len(hands)):
            #Create empty image with place for images
            hand_image = Image.new('RGB', (self.card_width*len(hands[hand_index]), self.card_height), color=(0, 80, 80))
            
            card_index = 0
            #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
            for card in [card for card in sorted(hands[hand_index], key=lambda c: c.to_int_runs())]:
                if show_index:
                    hand_image.paste(self.get_card(card, hands[hand_index].index(card)), (card_index*self.card_width, 0))
                else:
                    hand_image.paste(self.get_card(card, None), (card_index*self.card_width, 0))
                card_index += 1

            all_hands_img.paste(hand_image, (0, self.card_height*hand_index))

        #Return image path
        return self.surface_to_pil_image(pg.transform.rotozoom(self.pil_image_to_surface(all_hands_img), 0, self.sprite_scalar))
    
###############################################################################
# TODO: MUST IMPLEMENT BELOW FUNCTIONS
###############################################################################

#Returns an Image of the selected card
    def get_card(self, card:deck.Card, index:int=None) -> Image:
        pass