# split teams for futbol
import sys
import warnings
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import re


def get_players(args, show=True):
    """
    Get list of players
    """
    if len(args)>1:
        print ("\nName file detected\n")
        filename = args[1]

        with open(filename) as file:
            names = [line.rstrip() for line in file]

    else:
        names = []
        playernum = 1
        curname = input(f"Enter player {playernum}: ")
        while (len(curname)>0):
            names.append(curname)
            playernum += 1
            curname = input(f"Enter player {playernum}: ")

    # merge in positions
    positions = pd.read_csv("teammaker/POSITIONS.csv")

    joined = pd.merge(left = pd.DataFrame({"names":names}),
                      right= positions,
                      left_on = "names",
                      right_on= "Name",
                      how="left").drop("Name",axis=1).fillna("U", axis=1)

    if show is True:
        show_df(joined)
   
    return joined #names 


def show_df(df_ref, pos=False):
    """
    Pretty print dataframe
    Sort by position if pos
    """

    # TODO: do another join on POSITIONS.csv here (or take the already joined df as an arg)
    # Some positions are replaced during train_test_split for stratification purposes
    # Would be good to show real positions here

    df = df_ref.copy()

    #pos=False

    if pos is True:
        white = df['WHITE'].copy()
        dark = df['DARK'].copy()

        wnames = []
        wposis = []
        for w in white.str.replace(" (", "(", regex=False).str.split("("):
            wnames.append(w[0])
            wposis.append("("+w[1])

        dnames = []
        dposis = []
        for d in dark.str.replace(" (", "(", regex=False).str.split("("):
            dnames.append(d[0])
            dposis.append("("+d[1])
            

        white_df = pd.DataFrame({"name":wnames, "pos":wposis}).sort_values(by='pos',ignore_index=True)
        dark_df  = pd.DataFrame({"name":dnames, "pos":dposis}).sort_values(by='pos',ignore_index=True)
        
        white_df['concat'] = white_df['pos'] + " " + white_df['name']
        dark_df['concat']  = dark_df ['pos'] + " " + dark_df ['name']

        ndf = pd.DataFrame({})
        ndf['WHITE'] = [""]+list(white_df['concat'])
        ndf['DARK']  = [""]+list(dark_df ['concat'])
        ndf.drop(0, axis=0, inplace=True)

        df = ndf.copy()


    # for mo :)
    df.replace("(M) Mo", "(1) Mo", inplace=True)

    print()
    print(df.to_markdown())
    print()


def split_teams(players, show=True):
    """
    give list of players, split randomly into two
    Then give options to make changes, save, or re-roll
    """
     
    if len(players) % 2 == 1:
        warnings.warn("ODD number of players")

    
    show_df(players)

    is_split = True

    try:
        white, dark = train_test_split(players, test_size=0.5, stratify=players['Position'])
    except:
        warnings.warn("TOO FEW CLASSES")
        vc = players['Position'].value_counts().reset_index(name='count')
        print("HERE MAX")
        show_df(vc)
        [print(f"There is only one {c}") for c in vc[vc['count']==1]['index']]


        for c in vc[vc['count']==1]['index']:
            if c == "G":
                print("Replacing G with D")
                players['Position'].replace("G", "D", inplace=True)

            elif c == "W":
                print("Replacing W with F")
                players['Position'].replace("W", "F", inplace=True)

            elif c == "U":
                print("Replacing U with M")
                players['Position'].replace("U", "M", inplace=True)

            elif c == "F":
                print("Replacing F with M")
                players['Position'].replace("F", "M", inplace=True)

            else:
                print(f"ONLY ONE {c}, REPLACEMENT NOT IMPLEMENTED")

        try: 
            white, dark = train_test_split(players, test_size=0.5, stratify=players['Position'])
        except:
            print("splitting without positions...")
            is_split = False # mention if not split on positions
            white, dark = train_test_split(players, test_size=0.5)

    white = [""] + list((white['names'] + " (" + white['Position'] + ")"))
    dark = [""] + list((dark['names'] + " (" + dark['Position'] + ")"))

    print(white, flush=True)
    print(dark, flush=True)


    df = pd.DataFrame({"WHITE": white, "DARK":dark})

    df.drop(0, axis=0, inplace=True)


    if show is True:
        show_df(df, pos=True)

    return df, is_split


def adjust_teams(df, names_df):
    """
    Give options to make changes, re-roll, or finalize
    """
    inp = ""
    while (inp.lower() != 'f'):
        inp = str(input("Enter F to finalize, R to re-roll, S <white player> <dark player> to swap two players, or Q to quit: "))

        if inp.lower() == 'q':
            print("Quitting...")
            sys.exit(1)

        elif inp.lower() == 'r':
            print("Re-rolling df...")
            df = split_teams(names_df)

        elif inp.lower() == 'f':
            os.system('clear')
            show_df(df, pos=True) 

        elif inp.lower()[0] == 's':
            inp = inp[2:]
            args = inp.split(" & ")
            if len(args) != 2:
                print("BAD INPUT")
                print(args)
                continue

            else:
                print(args)

            try:
                white_player = args[0]
                dark_player = args[1]

                white_player = list(df[df['WHITE'].str.contains(white_player)]['WHITE'])[0]
                dark_player = list(df[df['DARK'].str.contains(dark_player)]['DARK'])[0]

            except:
                print("ISSUE WITH SWAP, format is: S <white_player> & <dark_player>")
                continue

            nw = df['WHITE'].replace(white_player, dark_player)
            nd = df['DARK'].replace(dark_player, white_player)

            # if changes made in white AND dark
            if any(nw != df['WHITE']) and any(nd != df['DARK']):
                df['WHITE'] = nw.copy()
                df['DARK'] = nd.copy()
                print(f"\n--SWAPPED {white_player} AND {dark_player}--\n")

            else:
                print(f"\n--NO SWAPS MADE (check spelling)--\n")

            show_df(df, pos=True)

        else:
            print("BAD INPUT")
            
    
if __name__ == '__main__':

    names_df = get_players(sys.argv, show=False)
    names = names_df['names']
    with open('players.txt', 'w') as f:
        for name in names:
            f.write(f"{name}\n")

    df = split_teams(names_df)

    df = adjust_teams(df, names_df)
