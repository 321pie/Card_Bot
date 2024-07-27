#Foreign Imports
import copy

#Local Imports
import deck
import print_hand


class Default_Print(print_hand.Print_Hand):
    def __init__(self):
        #The size of the sprites
        self.base_card_width = 32 #Excess room on sprite sheet
        self.base_card_height = 32 #Excess room on sprite sheet
        self.card_width = 32
        self.card_height = 48
        self.num_width = 16
        self.num_height = 16
        self.base_num_width = 9 * self.card_width + self.base_card_width
        self.base_num_height = 4 * self.card_height + self.base_card_height + 8
        self.sprite_scalar = 3

    #Get picture of hand using "all_assets" in "card_art"
    async def get_hand_pic(hands:list[list[deck.Card]], show_index=True):
        #If a single card is passed in, ignore index and just display the card.
        #Else, get hand if index is valid, or crib if index is negative.
        player_index = copy.copy(plyr_index)
        if card != None:
            print(card.display)
            hand = [copy.copy(card)]
        else:
            if player_index == -1:
                hand = crib
            else:
                try:
                    hand = hands[player_index]
                except:
                    print("Invalid player index in get_hand_pic.")
                    return ""
            

        asset_file_path = get_path('card_art\\all_assets.png')
        card_file_path = get_path('card_art\\card' + str(player_index) + '.png')
        index_file_path = get_path('card_art\\index' + str(player_index) + '.png')

        output_string = ""

        #Stores index number
        card_index = 0

        #Create empty image with place for images
        hand_image = Image.new('RGB', (card_width*len(hand)*sprite_scalar, card_height*sprite_scalar), color=(0, 80, 80))

        #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
        for card in [card for card in sorted(hand, key=lambda x: x.to_int_runs())]:
            if card.value != dk.JOKER:
                #Get right column
                width_multiplier = 4 * floor((card.to_int_runs()-1) / 3)

                #Get right sub-column based on suit
                if card.suit == dk.DIAMOND:
                    width_multiplier += 1
                if card.suit == dk.CLUB:
                    width_multiplier += 2
                if card.suit == dk.HEART:
                    width_multiplier += 3

                #Get right row
                height_multiplier = (card.to_int_runs()+2) % 3

            else:
                height_multiplier = 1
                width_multiplier = 16 #Fourth column * 4 cards in each column

                if card.suit == dk.RED:
                    width_multiplier += 1

            x_coord = card_width * width_multiplier + base_card_width
            y_coord = card_height * height_multiplier + base_card_height

            sheet = pg.image.load(asset_file_path)
            card_image = sheet.subsurface((x_coord, y_coord, card_width, card_height))

            pg.image.save(pg.transform.rotozoom(card_image, 0, sprite_scalar), card_file_path)

            card_img = Image.open(card_file_path)

            #Add index (![0-9]) to card
            if show_index == True:
                index_img = Image.new('RGB', (floor(card_width*sprite_scalar/2), floor(card_height*sprite_scalar/2)), color=(0, 0, 0))

                index = hand.index(card)

                if index != 0:
                    num_width_multiplier = (index+2) % 3
                    num_height_multiplier = floor((index-1) / 3)
                else:
                    num_width_multiplier = 1
                    num_height_multiplier = 3

                x_num_coord = num_width * num_width_multiplier + base_num_width
                y_num_coord = num_height * num_height_multiplier + base_num_height

                num_image = sheet.subsurface((x_num_coord, y_num_coord, num_width, num_height))

                pg.image.save(pg.transform.rotozoom(num_image, 0, sprite_scalar), index_file_path)

                index_img.paste(Image.open(index_file_path), (floor(card_width*sprite_scalar*3/16), floor(card_height*sprite_scalar*3/16)))
                card_img.paste(index_img, (floor(card_width*sprite_scalar/4), floor(card_height*sprite_scalar/4)))

                #Add index to output string
                output_string += "!" + str(index) + '\t  '

                #Delete created image
                os.remove(index_file_path)

            #Add card to line
            hand_image.paste(card_img, (card_index*card_width*sprite_scalar, 0))

            #Increment to next index
            card_index += 1

        #Ensure concurrency for when throwing away multiple cards in rapid succession
        try:
            if not os.path.exists(get_path('card_art\\hand' + str(player_index) + '.png')):
                hand_file_path = get_path('card_art\\hand' + str(player_index) + '.png')
            else:
                hand_file_path = get_path('card_art\\hand' + str(player_index + len(players)) + '.png')
        except:
            hand_file_path = get_path('card_art\\hand' + str(player_index + len(players)) + '.png')

        #Save hand image
        hand_image.save(hand_file_path)

        #Delete created image
        os.remove(card_file_path)

        #Return image path
        return hand_file_path

    #Get single picture with all hands in it
    async def get_all_hand_pics():
        global players
        global hands

        global base_card_width #Excess room on sprite sheet
        global base_card_height #Excess room on sprite sheet
        global card_width
        global card_height
        global num_width
        global num_height
        global base_num_width
        global base_num_height
        global sprite_scalar

        all_hands_file_path = get_path('card_art\\all_hands.png')

        #Stores index number
        hand_index = 0
        max_hand_len = 4

        for hand in hands:
            if len(hand) > max_hand_len:
                max_hand_len = len(hand)

        #Create empty image with place for images
        all_hands_img = Image.new('RGB', (card_width*max_hand_len*sprite_scalar, card_height*sprite_scalar*len(hands)), color=(0, 80, 80))

        #Create list of hand pics to delete
        hand_paths = []

        #For each card in the hand, retrieve it from the sprite sheet and add it to hand image
        for hand_index in range(len(hands)):
            #Extra variable because load doesn't like indexing into an array for some reason
            hand_paths.append(await get_hand_pic(hand_index))
            hand_img = Image.open(hand_paths[-1])

            all_hands_img.paste(hand_img, (0, card_height*sprite_scalar*hand_index))

        #Save massive hand pic
        all_hands_img.save(all_hands_file_path)

        #Delete created image
        for path in hand_paths:
            os.remove(path)

        #Return image path
        return all_hands_file_path