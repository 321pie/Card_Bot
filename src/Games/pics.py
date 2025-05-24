import copy
import io
import os
from PIL import Image, ImageDraw, ImageFont
import pygame as pg
from random import randrange

import Games.deck as deck


class pics():
    CLASSIC = "Classic"
    GENSHIN = "Genshin"
    CATS = "Cats"
    STARWARS = "Starwars"
    POKEMON = "Pokemon"
    ZELDA = "Zelda"
    HALLOWEEN = "Halloween"
    POP = "Pop"
    FRENCH = "French"
    
    def __init__(self, custom_deck):
        #The size of the sprites
        self.card_width = 315 #Width of each card
        self.card_height = 438 #Height of each card
        self.bar_height = 75 #Height of the bar that holds the index
        if custom_deck == "Pokemon":
            rng = randrange(0, 100)
            if rng <= 29:
                self.custom_deck = "Pokemon1"
            elif rng <= 59:
                self.custom_deck = "Pokemon2"
            elif rng <= 79:
                self.custom_deck = "PokemonS"
            else:
                self.custom_deck = "PokemonQ"

            rng = randrange(0, 100)
            if rng <= 9:
                self.custom_deck += "_Shiny"
        else:
            self.custom_deck = custom_deck
        #This one can change as needed
        self.sprite_scalar = .3 #Multiplier to zoom by to make hand a good size

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
    
    def surface_to_pil_image(self, surface:pg.Surface) -> Image.Image:
        pil_string_image = pg.image.tobytes(surface, "RGBA", False)
        return Image.frombytes("RGBA", (surface.get_width(), surface.get_height()), pil_string_image)
    
    #Get single picture with all hands in it
    def get_hand_pic(self, hands:list[list[deck.Card]], show_index=True):
        #Stores index number
        hand_index = 0
        max_hand_len = 0
        card_height = self.card_height

        if show_index:
            card_height += self.bar_height

        for hand in hands:
            if len(hand) > max_hand_len:
                max_hand_len = len(hand)

        #Create empty image with place for images
        if max_hand_len == 0:
            max_hand_len == 1
        hands_img = Image.new('RGB', (self.card_width*max_hand_len, card_height*len(hands)), color=(0, 0, 0))
 
        #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
        for hand_index in range(len(hands)):
                hand = hands[hand_index]
                handCopy = sorted(copy.copy(hand), key=lambda c: c.to_int_runs())
                #For each card in hand
                for card_index in range(len(hand)):
                    hands_img.paste(self.get_card(handCopy[card_index], hand.index(handCopy[card_index]), show_index), (card_index * self.card_width, hand_index * card_height))

        new_size = (int(self.card_width * max_hand_len * self.sprite_scalar), int(card_height*len(hands) * self.sprite_scalar))
        hands_img = hands_img.resize(new_size, Image.Resampling.LANCZOS)
        byte_image = io.BytesIO()
        hands_img.save(byte_image, format='PNG')
        byte_image.seek(0)

        #return image as byte array
        return byte_image
    
    #Returns an Image of the selected card
    def get_card(self, card:deck.Card, index:int, showIndex:bool=False) -> Image.Image:
        #Define path to assets
        try:
            asset_file_path = self.get_path(f'src\\card_art\\{self.custom_deck}_Deck.png')
            sprite_sheet = Image.open(asset_file_path)
        except:
            return None

        #Get values for card in sprite sheet
        if card.value != deck.JOKER:
            #Get right column
            column = card.to_int_runs()

            #Get right row
            if card.suit == deck.CLUB:
                row = 0
            elif card.suit == deck.DIAMOND:
                row = 1
            elif card.suit == deck.HEART:
                row = 2
            elif card.suit == deck.SPADE:
                row = 3
        #Jokers are in a different place, so get those
        else:
            row = 4

            if card.suit == deck.RED:
                column = 1
            else:
                column = 3

        left = self.card_width * (column - 1)
        top = self.card_height * row
        right = left + self.card_width
        bottom = top + self.card_height

        #Grab card from sprite sheet and save it
        card_img = sprite_sheet.crop((left, top, right, bottom))

        #Add index (![0-9]) to card
        if showIndex:
            #Create black rectangle that is slightly taller than card height
            index_card = Image.new('RGB', (self.card_width, self.card_height + self.bar_height), color=(0,0,0))

            #Paste card image so there is a bar under the card now
            index_card.paste(card_img, (0,0))

            draw = ImageDraw.Draw(index_card)
            try:
                if "Pokemon" in self.custom_deck:
                    font = ImageFont.truetype(f"src\\Font\\Pokemon_Font.ttf", 55)
                else:
                    font = ImageFont.truetype(f"src\\Font\\{self.custom_deck}_Font.ttf", 55)
            except:
                return None

            #Adding the text to bar
            text = "!" + str(index)
            draw.text((self.card_width / 2.2, self.card_height), text, font=font, fill=(255, 255,255))
            return index_card

        #Return image path
        return card_img