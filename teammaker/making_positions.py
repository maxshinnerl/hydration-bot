import  pandas  as pd
from make_teams import show_df

names = []
posis = []

while(True):
    name = str(input("Name of player, or enter QUIT to quit: ")).replace(" ","")
    if str(name).upper() == "QUIT":
        break
    pos = str(input("Position (G goalie, D defense, M midfield, W wing, F forward, U unknown) : ")).upper()

    if pos in ["G", "D", "M", "W", "F"]: 
        print(f"Adding ({pos}) {name}")
        names.append(name)
        posis.append(pos)

    else:
        print(f"invalid position, '{name}' not added")
   
try:
    df = pd.read_csv("POSITIONS.csv")
except:
    print("No positions.csv found, creating new..")
    df = pd.DataFrame({})
    

df = pd.concat([df, pd.DataFrame({"Name":names, "Position":posis})])
df.sort_values(by='Name', inplace=True)
df.to_csv("POSITIONS.csv", index=False)

# before showing, add more columns grouped by position for visualization
df_ = df.sort_values(by=['Position', 'Name']).reset_index(drop=True)

df['---'] = ['' for i in range(len(df))]
df['Position_'] = df_['Position'].copy()
df['Name_'] = df_['Name'].copy()

show_df(df.reset_index(drop=True))
