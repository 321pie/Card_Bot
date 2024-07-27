#Foreign Imports
from PIL import Image
import pygame as pg

#Local Imports
import Games.deck as deck
import Games.Prints.print_hand as ph


class Default_Print(ph.Print_Hand):
    def __init__(self):
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

    #Get single picture with all hands in it
    def get_hand_pic(self, hands:list[list[deck.Card]], show_index=True) -> Image:
        #Stores index number
        hand_index = 0
        max_hand_len = 0

        for hand in hands:
            if len(hand) > max_hand_len:
                max_hand_len = len(hand)

        #Create empty image with place for images
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