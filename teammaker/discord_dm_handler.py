# Parse DM for list of players
# Return error message if message does not contain a numbered list.

import re
from teammaker import make_teams
def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


def dm_handler(message):

    print("DM RECEIVED:", message, flush=True)

    if ("1." not in message.content) and ("1)" not in message.content):
        raise ValueError # respond with default message
        
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

    end = len(players) # default
    # update if there are waitlist rows
    for i,line in enumerate(players):
        if has_numbers(line) and (("." in line) or (")" in line)):
            continue
        else:
            end = i
            break

                
    players = players[:end]

    newplayers = []
    for player in players:
        np = ''.join([i for i in player if not i.isdigit()])
        np = re.sub(r'[^\w+]+', '', np)
        newplayers.append(np)

    with open('teammaker/players.txt', 'w') as f:
        for name in newplayers:
            f.write(f"{name}\n")

    # Pass to teammaker code
    print("getting players..", flush=True)
    names_df = make_teams.get_players([None, "teammaker/players.txt"], show=False)

    print("splitting teams..", flush=True)
    df, is_split = make_teams.split_teams(names_df)

    # TODO allow re-roll, swap, finish, etc. to be inputted from discord
    #df = make_teams.adjust_teams(df, names_df)

    make_teams.show_df(df, pos=True) # added ret argument for this specifically
                                                    # just gets the pretty DF back as a string

    response = "WHITE\n"
    response += "\n".join(df['WHITE'])

    response += "\n\nDARK\n"
    response += "\n".join(df['DARK'])
       
    print(response)

    return response, is_split
