# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random

first_line = True # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]
last_me_before = "?"
last_them_before = "?"
prediction = {"RR":"?", "RP":"?", "RS":"?", "PR":"?", "PP":"?", "PS":"?", "SR":"?", "SP":"?", "SS":"?"}
letter_permutation = { "R" : "P", "P" : "S", "S": "R"}
enough_health = True # makes player go home if true and health drops too low
counter = 0

movement_map = {
    "0" : 10,
    "1" : 1,
    "2" : 6,
}

def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"
    else:
        return "Rock"

def get_losing_stance(stance):
    if stance == "Rock":
        return "Scissors"
    elif stance == "Paper":
        return "Rock"
    elif stance == "Scissors":
        return "Paper"
    else:
        return "Rock"

# main player script logic
# DO NOT CHANGE BELOW ----------------------------
for line in fileinput.input():
    if first_line:
        game = game_API.Game(json.loads(line))
        first_line = False
        continue
    game.update(json.loads(line))
# DO NOT CHANGE ABOVE ---------------------------
# code in this block will be executed each turn of the game

    chosen_stance = "?"
    destination_node = ""
    # first monster is weak to Rock
    if game.get_turn_num() == 1:
        chosen_stance = "Rock"

    #gets the player
    me = game.get_self()
    
    # reset boolean for retreat if health is gained
    if me.health >= 40:
        enough_health = True
    # retreat if health dips too low
    if enough_health and me.health < 40:
        destination_node = game.shortest_paths(me.location, 0)[0][0]
        enough_health = False
    # if destination was reached
    elif me.destination == me.location:
        # continue retreat
        if me.health < 35:
            destination_node = game.shortest_paths(me.location, 0)[0][0]
        # "flux capacitor" motion
        else:
            if me.location == 0:
                destination_node = movement_map[str(counter)]
                counter = (counter + 1)%3
            else:
                destination_node = 0
    else:
        destination_node = me.destination

    #finds the opponent
    opponent = game.get_opponent()

    # add prediction data based off last stances and current opponent stance
    if game.get_monster(opponent.location).dead and (game.get_turn_num() != 1) and (opponent.location == me.location):
        prediction_key = last_me_before.upper()[0:1] + last_them_before.upper()[0:1]
        prediction[prediction_key] = opponent.stance
    
    # create key to make current prediction
    current_key = me.stance.upper()[0:1] + opponent.stance.upper()[0:1]

    # create prediction
    for key in prediction:
        if key == current_key:
            first = key[0:1]
            last = key[1:2]
            # alternate keys if first one is not filled yet
            option1 = prediction[first + letter_permutation[last]]
            option2 = prediction[first + letter_permutation[letter_permutation[last]]]
            if prediction[key] != "?":
                chosen_stance = get_winning_stance(prediction[key])
            elif option1 != "?":
                chosen_stance = get_winning_stance(option1)
            elif option1 != "?":
                chosen_stance = get_winning_stance(option2)
            break
            
    # if no predicion was made
    if chosen_stance == "?":
        chosen_stance = get_winning_stance(opponent.stance)

    # fight monster if they are on the same tile
    if game.nearest_monsters(0, 1):
        for x in game.nearest_monsters(0, 1):
            if x.location == me.location:
                chosen_stance = get_winning_stance(game.get_monster(me.location).stance)

    # search for nearby monsters
    if game.nearest_monsters(me.location, 1):
        for x in game.nearest_monsters(me.location, 1):
            # if monster is on player's same tile, fight it
            if x.location == me.location:
                # if monster is not killed, stay here
                if me.movement_counter == 1:
                    destination_node = me.location
                chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
            # get ready to fight if monster is on destination node
            elif x.location == destination_node and me.movement_counter == 0:
                chosen_stance = get_winning_stance(game.get_monster(destination_node).stance)

    # set data for next turns prediction data entry
    last_me_before = me.stance
    last_them_before = opponent.stance

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(destination_node, chosen_stance)
