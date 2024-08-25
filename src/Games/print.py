from PIL import Image, ImageDraw, ImageFont
import pygame as pg
import os
import deck
import copy

class Print():
    def __init__(self):
        #The size of the sprites
        self.card_width = 158 #Width of each card
        self.card_height = 221 #Height of each card
        self.CLASSIC = "Classic"
        self.GENSHIN = "Genshin"
        self.CATS = "Cats"
        self.STARWARS = "Starwars"

        #This one can change as needed
        self.sprite_scalar = 1 #Multiplier to zoom by to make hand a good size

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
    def get_hand_pic(self, hands:list[list[deck.Card]], customDeck:str="Classic", show_index=True) -> Image:
        #Stores index number
        hand_index = 0
        max_hand_len = 0
        card_height = self.card_height

        if show_index:
            card_height += 50

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
                    hands_img.paste(self.get_card(handCopy[card_index], hand.index(handCopy[card_index]), customDeck, show_index), (card_index * self.card_width, hand_index * card_height))
                    
        #Return image path
        hands_img.show()
        return self.surface_to_pil_image(pg.transform.rotozoom(self.pil_image_to_surface(hands_img), 0, self.sprite_scalar))
    
#Returns an Image of the selected card
    def get_card(self, card:deck.Card, index:int, customDeck:str="Classic", showIndex:bool=False) -> Image:
        #Define path to assets
        try:
            asset_file_path = self.get_path(f'src\\card_art\\{customDeck}_Deck.png')
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
            row = 5 #5th row

            if card.suit == deck.RED:
                column = 1
            else:
                column = 3

        x_coord = self.card_width * (column - 1) 
        y_coord = self.card_height * row

        #Grab card from sprite sheet and save it
        sheet = pg.image.load(asset_file_path)
        card_image = sheet.subsurface((x_coord, y_coord, self.card_width, self.card_height))

        card_image = self.surface_to_pil_image(card_image)

        #Add index (![0-9]) to card
        if showIndex:
            bar_height = 50
            #Create black rectangle that is slightly taller than card height
            index_card = Image.new('RGB', (self.card_width, self.card_height + bar_height), color=(0,0,0))

            #Paste card image so there is a bar under the card now
            index_card.paste(card_image, (0,0))

            draw = ImageDraw.Draw(index_card)
            try:
                font = ImageFont.truetype(f"src\\Font\\{customDeck}_Font.ttf", 40)
            except:
                return None

            #Adding the text to bar
            text = "!" + str(index)
            draw.text((self.card_width / 2.5, self.card_height - 5), text, font=font, fill=(255, 255,255))
            return index_card

        #Return image path
        return card_image