# Parse DM for list of players
# Return error message if message does not contain a numbered list.

import re
from teammaker import make_teams
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
                continue
            else:
                end = i
                break
                

        players = players[:end]

        newplayers = []
        for player in players:
            np = ''.join([i for i in player if not i.isdigit()])
            np = re.sub(r'\W+', '', np)
            newplayers.append(np)


        with open('teammaker/players.txt', 'w') as f:
            for name in newplayers:
                f.write(f"{name}\n")

        # Pass to teammaker code
        names_df = make_teams.get_players([None, "teammaker/players.txt"], show=False)

        df = make_teams.split_teams(names_df)

        # TODO allow re-roll, swap, finish, etc. to be inputted from discord
        #df = make_teams.adjust_teams(df, names_df)

        df = make_teams.show_df(df, pos=True, ret=True)

        response = "WHITE\n"
        response += "\n".join(df['WHITE'])

        response += "\n\nDARK\n"
        response += "\n".join(df['DARK'])
       

        return response
