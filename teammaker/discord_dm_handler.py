# Parse DM for list of players
# Return error message if message does not contain a numbered list.

import re
def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


def dm_handler(message):

    if ("1." not in message.content) and ("1)" not in message.content):
        resposne = "No list detected--order list with 1. 2. 3. or 1) 2) 3)"

    else:
        
        players = message.content.split("\n")
        if len(players) > 100:
            return "Too many lines in message (max 100)"

        start = 0
        for p in players:
            if ("1." not in p) and ("1)" not in p):
                start += 1

            else:
                break

        players = players[start:]
        end = len(players) - 1
        for i,line in enumerate(players):
            if has_numbers(line) and (("." in line) or (")" in line)):
                print(line, flush=True)
                continue
            else:
                end = i
                break
                

        players = players[:end]

        # TODO pass players list ^ to the existing teammakers code
        # TODO allow re-roll, swap, finish, etc. to be inputted from discord

        response = "\n".join(players)



    return response
