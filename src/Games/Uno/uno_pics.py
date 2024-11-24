from PIL import Image, ImageDraw, ImageFont

from Games.Uno.uno_deck import Card
from Games.pics import Pics

class UnoPics(Pics):

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

        #Add index (![0-9]) to card
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

