#Foreign imports
import itertools
import copy
import time
from collections import OrderedDict

#Local imports
import deck


#Finding Nibs  
def nibs(flipped):
    points = 0

    #For Nibs (flipping a jack)
    if flipped.value == deck.VALUES[-3]:
        points += 2

    return points

#Check points for counting, with cur_card NOT in old_cards, but cur_card IS included in sum
def check_points(cur_card, old_cards, sum):
    points = 0
    if(len(old_cards) >= 2): #Find longest run if enough cards
        complete_run = True
        total_card_index = 2
        while(total_card_index <= len(old_cards)):
            #Populate card list for runs, starting with 3 and incrementing until run is broken or there are no more cards
            cards = [cur_card.to_int_runs()]
            for card_index in range(1, total_card_index+1):
                cards.append(old_cards[-card_index].to_int_runs())

            #sort cards to determine run and increment total_caard_index for next iteration
            cards = sorted(cards, reverse=True)
            total_card_index += 1

            #See if run is valid
            for ii in range(len(cards)-1):
                if(cards[ii]-1 != cards[ii+1]):
                    complete_run = False
                    break

            #If valid run, get number of points and reset complete_run
            if(complete_run == True):
                points = len(cards)
            complete_run = True

    if(len(old_cards) >= 1):
        if(cur_card.value == old_cards[-1].value): #Check for pair
            points += 2
            if(len(old_cards) >= 2):
                if(cur_card.value == old_cards[-2].value): #Check for double pair (3 of a kind)
                    points += 4 #2 + 4 = 6
                    if(len(old_cards) >= 3):
                        if(cur_card.value == old_cards[-3].value): #Check for double pair (3 of a kind)
                            points += 6 #6 + 6 = 12

    if(sum == 15 or sum == 31): #Check for 15 and 31
        points += 2

    return points

#Finding Nobs
def nobs(hand, flipped, points=0, output_string=''):
    #For Nobs (suit of jack in hand matches the flipped suit)
    for card in hand:
        if card.suit == flipped.suit and card.value == deck.VALUES[-3]:
            output_string += "Nobs for 1\n"
            points += 1
            break

    return [points, output_string]

#Finding 15s
def find_15s(hand, flipped, points=0, output_string=''):
    hand = copy.copy(hand)
    hand.append(flipped)

    for subset_size in range(1, len(hand) + 1):
        for subset in itertools.combinations(hand, subset_size):
            subset_sum = sum(card.to_int_15s() for card in subset)

            if subset_sum == 15:
                points += 2
                subset_expression = " + ".join(f"{card.value}" for card in subset)
                output_string += f"{subset_expression} = 15 ({points})\n"
                
    return [points, output_string]

#Finding Pairs
def find_pairs(hand, flipped, points=0, output_string=''):
    hand = copy.copy(hand)
    hand.append(flipped)

    for card1, card2 in itertools.combinations(hand, 2):
        if card1.value == card2.value:
            points += 2
            output_string += f"Pair {card1.value} / {card2.value} ({points})\n"
            
    return [points, output_string]

#Finding Runs
def find_runs(hand, flipped, points=0, output_string=''):
    #Initialize list of card values
    hand = copy.copy(hand)
    hand.append(flipped)
    hand.sort(key=lambda card: card.to_int_runs(), reverse=True)
    card_values = [card.to_int_runs() for card in hand]
    
    #Set up variables
    multiplier_count = 0 #Counts duplicates in runs for displaying
    total_multiplier = 1 #Total run multiplier (duplicates)
    multiplier = 1 #Local multiplier (duplicates)
    run_length = 1 #Length of the current run

    #Loop through each card
    for index in range(len(card_values)):
        if(index+1 < len(card_values)): #Ensure that overflow doesn't occur
            if(card_values[index] == card_values[index+1]): #If duplicate, add to multiplier
                multiplier += 1
            else:
                if(card_values[index] != card_values[index+1] and multiplier > 1): #If duplicate needs resetting
                    multiplier_count += multiplier-1
                    total_multiplier *= multiplier
                    multiplier = 1
                if(card_values[index]-1 == card_values[index+1]): #If next card continues run (since duplicates are taken care of)
                    run_length += 1
                elif(run_length >= 3): #If valid run, add points, display, and reset variables
                    multiplier_count += multiplier-1
                    total_multiplier *= multiplier
                    points += run_length * total_multiplier
                    output_string += f"{total_multiplier} run(s) of {run_length}{list(OrderedDict.fromkeys([card.value for card in sorted([hand[i] for i in range(index+1-run_length-multiplier_count, index+1)], key=lambda card: card.to_int_runs())]))} for {run_length * total_multiplier} ({points})\n"

                    multiplier_count = 0
                    total_multiplier = 1
                    multiplier = 1
                    run_length = 1
                else: #If invalid run, reset variables
                    multiplier_count = 0
                    total_multiplier = 1
                    multiplier = 1
                    run_length = 1
        else: #If no more cards after this one, wrap up with current variables
            if(run_length >= 3):
                multiplier_count += multiplier-1
                total_multiplier *= multiplier
                points += run_length * total_multiplier
                output_string += f"{total_multiplier} run(s) of {run_length}{list(OrderedDict.fromkeys([card.value for card in sorted([hand[i] for i in range(index+1-run_length-multiplier_count, index+1)], key=lambda card: card.to_int_runs())]))} for {run_length * total_multiplier} ({points})\n"
                
            #Reset variables just to be safe
            multiplier_count = 0
            total_multiplier = 1
            multiplier = 1
            run_length = 1

    return [points, output_string]

#Finding Flush
def find_flush(hand, flipped, points=0, output_string='', isCrib = False):
    first_suit = hand[0].suit
    local_points = 0

    if all(card.suit == flipped.suit for card in hand):
        local_points += len(hand) + 1
    elif(not isCrib):
        if all(card.suit == first_suit for card in hand):
            local_points += len(hand)

    if(local_points != 0):
        points += local_points
        output_string += f"Flush of {first_suit} for {local_points}\n"

    return [points, output_string]

#Calculate the score for a hand
def calculate_hand(hand, flipped):
    startTime = time.time()
    points = 0
    output_string = ""

    #Organize the hand
    hand = sorted(hand, key=lambda x: x.value)
    
    output_string += f"Flipped:\n{flipped.value}\n\nHand:\n"
    for card in reversed(hand):
        output_string += f"{card.value}\n"
    
    output_string += "------------------------\n"

    #Calculate points
    [points, output_string] = find_15s(hand, flipped, points, output_string)
    [points, output_string] = find_pairs(hand, flipped, points, output_string)
    [points, output_string] = find_runs(hand, flipped, points, output_string)
    [points, output_string] = find_flush(hand, flipped, points, output_string)
    [points, output_string] = nobs(hand, flipped, points, output_string)

    output_string += "------------------------\n"
    output_string += f"Total points: {points}"

    endTime = time.time()

    # print(output_string)
    # print(f"\nCalculationTime: {endTime - startTime}s")

    return points, output_string

#Calculate the score for a crib
def calculate_crib(hand, flipped):
    startTime = time.time()
    points = 0
    output_string = ""

    #Organize the hand
    hand = sorted(hand, key=lambda x: x.value)
    
    output_string += f"Flipped:\n{flipped.value}\n\nCrib:\n"
    for card in reversed(hand):
        output_string += f"{card.value}\n"
    
    output_string += "------------------------\n"

    #Calculate points
    [points, output_string] = find_15s(hand, flipped, points, output_string)
    [points, output_string] = find_pairs(hand, flipped, points, output_string)
    [points, output_string] = find_runs(hand, flipped, points, output_string)
    [points, output_string] = find_flush(hand, flipped, points, output_string, True)
    [points, output_string] = nobs(hand, flipped, points, output_string)

    output_string += "------------------------\n"
    output_string += f"Total points: {points}"

    endTime = time.time()

    # print(output_string)
    # print(f"\nCalculationTime: {endTime - startTime}s")

    return points, output_string