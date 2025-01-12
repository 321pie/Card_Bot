import copy
import io
import math
from PIL import Image, ImageDraw, ImageFont

from Games.Uno.uno_deck import Card
from Games.pics import Pics

class UnoPics(Pics):
    def __init__(self):
        #The size of the sprites
        self.card_width = 315 #Width of each card
        self.card_height = 438 #Height of each card
        self.bar_height = 75 #Height of the bar that holds the index
        self.sprite_scalar = .3 #Multiplier to zoom by to make hand a good size
        self.hand_length = 8 #Length of the hand in the picture before it wraps

    #Override
    #Returns an Image of the selected card
    def get_card(self, card:Card, index:int, showIndex:bool=False) -> Image.Image:
        #Define path to assets
        try:
            asset_file_path = self.get_path(f'src\\card_art\\Uno_Deck.png')
            sprite_sheet = Image.open(asset_file_path)
        except:
            return None

        #Get values for card in sprite sheet
        #Get right column
        column = card.to_int_runs()

        #Get right row
        if card.value.find("wild") != -1:
            row = 4
        else:
            if card.color == "red":
                row = 0
            elif card.color == "blue":
                row = 1
            elif card.color == "yellow":
                row = 2
            elif card.color == "green":
                row = 3

        left = self.card_width * column
        top = self.card_height * row
        right = left + self.card_width
        bottom = top + self.card_height

        #Grab card from sprite sheet and save it
        card_img = sprite_sheet.crop((left, top, right, bottom))

        #Add index (![0-9]*) to card
        if showIndex:
            #Create black rectangle that is slightly taller than card height
            index_card = Image.new('RGB', (self.card_width, self.card_height + self.bar_height), color=(0,0,0))

            #Paste card image so there is a bar under the card now
            index_card.paste(card_img, (0,0))

            draw = ImageDraw.Draw(index_card)
            try:
                font = ImageFont.truetype(f"src\\Font\\Classic_Font.ttf", 55)
            except:
                return None

            #Adding the text to bar
            text = "!" + str(index)
            draw.text((self.card_width / 2.2, self.card_height), text, font=font, fill=(255, 255,255))
            return index_card

        #Return image path
        return card_img
    
    #Override
    #Get single picture with all your cards that are wrapped
    def get_hand_pic(self, hands:list[list[Card]], show_index=True) -> io.BytesIO:
        #Stores index number
        hand_length = self.hand_length
        card_height = self.card_height
        rows = math.ceil(len(hands[0]) / self.hand_length)

        if len(hands[0]) < hand_length:
            hand_length = len(hands[0])

        if show_index:
            card_height += self.bar_height

        hands_img = Image.new('RGB', (self.card_width* self.hand_length, card_height* rows), color=(0, 0, 0))

        handCopy = self.get_sorted_hand(hands[0])

        #For each card in hand
        for card_index in range(len(hands[0])):
            hands_img.paste(self.get_card(handCopy[card_index], hands[0].index(handCopy[card_index]), show_index), ((card_index % self.hand_length) * self.card_width, math.floor(card_index / self.hand_length) * card_height))

        new_size = (int(self.card_width * self.hand_length * self.sprite_scalar), int(card_height*rows * self.sprite_scalar))
        hands_img = hands_img.resize(new_size, Image.Resampling.LANCZOS)
        byte_image = io.BytesIO()
        hands_img.save(byte_image, format='PNG')
        byte_image.seek(0)

        #return image as byte array
        return byte_image

    def get_sorted_hand(self, hand):
        return sorted(copy.copy(hand), key=lambda c: (c.color, c.value))
