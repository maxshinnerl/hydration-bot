# Lowest level hydration bot functions file, specifically for DESTINY stuff
import json
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import difflib

import helpers

def get_weapon_stats(weapon_name, all_data, weapon_dict):
    """
    Internal function to avoid repeated code
    Do the grunt work getting weapon stats
    The wrapper functions (called from command_handling) will do the output formatting
    (and also call this function)
    """

    try:
        weapon_data = weapon_dict[weapon_name][0]  # sorted so first one is most relevant if applicable
    except:
        print("bad key:", weapon_name, flush=True)

    stats = {}
    for _, info in list(weapon_dict[weapon_name][0]['stats']['stats'].items()):
        # NOTE: if a weapon actually has a zero in a real stat, might want to adjust this code
        # current purpose is to omit "attack", "power", and other weird stats that aren't important
        stats["Name"] = weapon_name
        stats["Type"] = weapon_dict[weapon_name][0]['itemTypeAndTierDisplayName']

        if info['value'] != 0:
            stat_name = all_data['DestinyStatDefinition'][info['statHash']]['displayProperties']['name']
            stats[stat_name] = info['value']

    # pop unhelpful stats
    stats.pop('', None)
    stats.pop('Inventory Size', None)

    return stats


def weapstat(message, args, client, all_data, weapon_dict):
    """
    Get weapon stats for given weapon
    """

    #weapon_name = " ".join(args)
    weapon_name = get_closest_gun(message, args, client, all_data, weapon_dict)[0]

    stats = get_weapon_stats(weapon_name, all_data, weapon_dict)

    # no need for return arguments, just need to format the output
    response = ""
    for name, val in list(stats.items()):
        response += name + ": " + str(val) + "\n"

    return response


def recoil(message, args, client, all_data, weapon_dict):
    """
    Similar to weapstat, but only gives recoil direction
    Gives recommendation on counterbalance mod.
    """

    #weapon_name = " ".join(args)
    weapon_name = get_closest_gun(message, args, client, all_data, weapon_dict)[0]

    stats = get_weapon_stats(weapon_name, all_data, weapon_dict)

    if "Recoil Direction" not in stats.keys():
        return "No recoil listed for given weapon"

    rd = stats["Recoil Direction"]
    response = "Name: " + stats["Name"] + "\n" + \
               "Type: " + stats["Type"] + "\n" + \
               "Recoil Direction: " + str(rd) + "\n"

    bad_types = ["Shotgun", "Sniper Rifle", "Grenade Launcher", "Rocket Launcher", "Combat Bow"]

    # make recommendation
    if weapon_dict[weapon_name][0]['inventory']['tierTypeName'] == "Exotic":
        rec = "Cannot equip mods on exotics" 

    elif weapon_dict[weapon_name][0]['itemTypeDisplayName'] in bad_types:
        rec = "No: not recommended on a " + weapon_dict[weapon_name][0]['itemTypeDisplayName']

    elif rd == 100:
        rec = "NO. Recoil direction is maxed out"

    elif rd >= 97:
        rec = "No, recoil direction is high enough"

    elif (rd > 92) and (rd < 97):
        rec = "No, close to 95 and high enough already"

    elif (rd > 87) and rd <= 92:
        rec = "Maybe. It would help slightly, but base is high enough to justify other mods"

    elif int(str(rd)[-1]) in [4, 5, 6]:
        rec = "NO. Current recoil direction is vertical"

    elif int(str(rd)[-1]) in [0, 1, 9]:
        rec = "YES.  Highly recommended"

    elif int(str(rd)[-1]) in [2, 8]:
        rec = "Maybe: slight improvement, but other mods could be better"

    else:
        # ends in 3 or 7 -- cb mod brings to 8 or 2 which is worse
        rec = "No, would likely be around the same"

    response += "Counterbalance Mod Recommendation: " + rec

    return response

    
def compare(message, args, client, all_data, weapon_dict):
    """
    Pass in two weapon names and generate visualization on stats
    """
    # first need to extract weapon names (remember some are multiple words)
    # split on & sign

    w1, w2 = helpers.split_names(args)
    
    w1 = get_closest_gun(message, w1, client, all_data, weapon_dict)[0]
    w2 = get_closest_gun(message, w2, client, all_data, weapon_dict)[0]

    w1_stats = get_weapon_stats(w1, all_data, weapon_dict)
    w2_stats = get_weapon_stats(w2, all_data, weapon_dict)
    
    if w1_stats.keys() != w2_stats.keys():
        response = "Weapons too different to compare"
        return response
    
    labels = list(w1_stats.keys())[2:]
    w1_values = [w1_stats[key] for key in labels]
    w2_values = [w2_stats[key] for key in labels]

    labels.reverse()
    w1_values.reverse()
    w2_values.reverse()
    
    x = np.arange(len(labels)) * 2
    width = 0.7
    
    fig, ax = plt.subplots(figsize=(10,6))
    rects1 = ax.barh(x - width/2, w1_values, width, align='edge', label=w1)
    rects2 = ax.barh(x + width/2, w2_values, width, align='edge', label=w2)
    
    ax.set_title('Stat Comparison of ' + w1 + ' and ' + w2)
    ax.set_yticks(x)
    ax.set_yticklabels(labels)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), loc='upper right')
    
    for rect1, rect2 in zip(rects1, rects2):
        ax.text(rect1.get_width(), rect1.get_y()+0.15, rect1.get_width())
        ax.text(rect2.get_width(), rect2.get_y()+0.15, rect2.get_width())
    
    fig.tight_layout()

    plt.savefig("images/comp.png")
    
    return "Generated"
    

def sametype(message, args, client, all_data, weapon_dict):
    """
    Take in a weapon name, get all other weapons in the game of the same archetype
    Ordered by rarity, then alphabetical
    
    Note: Devil's Ruin and Vex Mythoclast have both Charge and RPM
    Will prioritize RPM in this case.  annoying lol
    """

    # name = " ".join(args)
    name = get_closest_gun(message, args, client, all_data, weapon_dict)[0]

    stats = get_weapon_stats(name, all_data, weapon_dict)
    weap_type = weapon_dict[name][0]['itemTypeDisplayName']
    
    if name == "Vex Mythoclast":
        # lol
        weap_type = "Auto Rifle"
    
    if "Rounds Per Minute" in stats.keys():
        rof = "Rounds Per Minute"
        
    elif "Charge Time" in stats.keys():
        rof = "Charge Time"
    
    else:
        print('weird -- No RPM or Charge Time')
        return
    
    samesies = []
    for w in weapon_dict.keys():
        if w == name or w == "Vex Mythoclast":
            # bite me
            continue
            
        if weapon_dict[w][0]['itemTypeDisplayName'] == weap_type:
            temp_stats = get_weapon_stats(w, all_data, weapon_dict)
            if temp_stats[rof] == stats[rof]:
                rarity = weapon_dict[w][0]['inventory']['tierTypeName']
                rarity_int = weapon_dict[w][0]['inventory']['tierType']
                samesies.append((w, rarity, rarity_int))
            
    if len(samesies) == 0:
        return("One of a kind!")

    samesies.sort(key=lambda x: (-x[2], x[0]))
    
    # Formulate response
    response = weap_type + " | " + rof + ": " + str(stats[rof]) + "\n" 
    last_type = ""
    for wtup in samesies:
        if wtup[1] != last_type:
            last_type = wtup[1]
            response += "\n**" + wtup[1].upper() + "**\n"
            
        response += wtup[0] + "\n"

    return(response)   


def perk(message, args, client, all_data, perk_dict):
    """
    Given the dictionary of perks, get info on the perk in question.
    Name, description, and boosted stats if applicable.
    """

    response = ""

    name = " ".join(args)

    if len(name) < 3:
        return None

    stat_list = perk_dict[name]

    if len(stat_list) > 1:
        response += "Multiple results found, here's the first one:\n\n"

    response += "**Perk Name**\n" + name
    response += "\n\n**Description**\n" + stat_list[0]['displayProperties']['description']
    response += "\n\n**Stats**"

    stats = stat_list[0]['investmentStats']

    if len(stats) == 0:
        response += "\nNone"

    else:
        for stat in stats:
            response += "\n  • "
            statname = all_data['DestinyStatDefinition'][stat['statTypeHash']]['displayProperties']['name']
            statval  = str(stat['value'])
            if statval[0] != "-":
                statval = "+" + statval
            response += statname + ": "  + statval

    return response


def rolls(message, args, client, all_data, weapon_dict, retstr=True):
    """
    get all possible perk rolls for a given weapon
    """

    #weapon = " ".join(args)
    weapon = get_closest_gun(message, args, client, all_data, weapon_dict)[0]

    repeats = 1
    rolls = {}
    weaptype = weapon_dict[weapon][0]['itemTypeAndTierDisplayName']
    
    # for socket (usually barrels, mags, perk1, perk2, etc)
    for socket in weapon_dict[weapon][0]['sockets']['socketEntries']:
        # if random rolls
        if "randomizedPlugSetHash" in socket.keys():
            randhash = socket['randomizedPlugSetHash']
            sockethash = socket['socketTypeHash']
            socketname = all_data['DestinySocketTypeDefinition'][sockethash]['plugWhitelist'][0]['categoryIdentifier']
        
            # for every perk that goes in that socket for this weapon
            perks = set()
            for perk in all_data['DestinyPlugSetDefinition'][randhash]['reusablePlugItems']:
                itemhash = perk['plugItemHash']
                perks.add(all_data['DestinyInventoryItemDefinition'][itemhash]['displayProperties']['name'])
                
            # save list of perks for each socket name
            if socketname == "frames":
                socketname = "Main Perk " + str(repeats)
                repeats += 1
            else:
                socketname = socketname[0].upper() + socketname[1:]
                
            rolls[socketname] = list(perks)


    if retstr is True:
        return(rolls_format(rolls, weapon, weaptype))

    return rolls # can specify retstr = False in parameters if you just want the dict back.
    

def rolls_format(rolls, weapon, weaptype):
    """
    Get the response
    """
    response = "**Weapon**\n" + weapon + " : " + weaptype + "\n\n"
    
    for key in rolls.keys():
        response += f"**{key}**\n"
        for perk in rolls[key]:
            response += perk + "\n"
        response += "\n"

    response += "See the $perk command for details on any of the above"
    return response


def rollable(weapon, weapon_dict, all_data):
    """
    Return true if weapon is legendary and is not sunset
    """
    if (weapon_dict[weapon][0]['inventory']['tierType'] == 5) & \
       (all_data['DestinyPowerCapDefinition'][weapon_dict[weapon][0]['quality']['versions'][0]['powerCapHash']]['powerCap'] == 999990):
        
        return True
    
    return False


# TODO.  I'm not sure how to find possible masterworks, it's encoded pretty weirdly.
def masterworks(weapon, weapon_dict):
    """
    Return possible masterworks for a weapon.
    """
    
    # ok I give up, I'm hardcoding the masterworks dict
    """
    Guide:
    0 -- normal (basically anything that shoots bullets)
    1 -- fusions (normal + charge time)
    2 -- bows (normal - range + accuracy + draw time)
    3 -- explosives (normal - range + velocity + blast radius)
    4 -- sword (impact only)
    """

    mw_dict = {
               0:["Range", "Stability", "Handling", "Reload Speed"],
               1:["Range", "Stability", "Handling", "Reload Speed", "Charge Time"],
               2:["Stability", "Handling", "Reload Speed", "Draw Time", "Accuracy"],
               3:["Stability", "Handling", "Reload Speed", "Velocity", "Blast Radius"],
               4:["Impact"],
               5:["Range", "Handling", "Reload Speed", "Shield Duration"]
              }
    
    arch = weapon_dict[weapon][0]['itemTypeDisplayName']
    
    
    # tree time baby
    if "Fusion" in arch:
        arch_hash = 1
    
    elif "Bow" in arch:
        arch_hash = 2
        
    elif "Launcher" in arch:
        arch_hash = 3
        
    elif "Sword" in arch:
        arch_hash = 4

    elif "Glaive" in arch:
        arch_hash = 5
    
    else:
        arch_hash = 0
        
    return mw_dict[arch_hash]


def get_icon(path):
    """
    Go to weapon icon url and download it into images/icon.png
    """
    
    path = "https://www.bungie.net" + path
    r = requests.get(path)
    with open("images/icon.png", 'wb') as f:
        f.write(r.content)


# in production this will need the usual params
def engram(all_data, weapon_dict):
    """
    Random roll, random legendary (non-sunset)
    """
    legendary_dict = {k:v for k,v in weapon_dict.items() if rollable(k, weapon_dict, all_data)}
    
    # perks command is bugged, some weapons return empty.  This just re-rolls until you get a good one.
    # temporary fix
    
    perks = {}
    while (len(perks.keys()) == 0):   
    
        rand = np.random.randint(len(legendary_dict))
        randweap = list(legendary_dict.keys())[rand]
        perks = rolls(None, randweap.split(" "), None, all_data, weapon_dict, retstr=False)

    response = randweap
    arch = weapon_dict[randweap][0]['itemTypeDisplayName']
    response += " : " + arch + "\n"
    
    
    for key in perks.keys():
        rand = np.random.randint(len(perks[key]))
        response += perks[key][rand] + " | "
        
    response = response[:-3]
        
    # get masterwork
    mw_list = masterworks(randweap, weapon_dict)
    rand = np.random.randint(len(mw_list))
    rand_mw = mw_list[rand]
    
    response += "\nMasterwork: " + rand_mw
    
    # get PNG of weapon
    get_icon(weapon_dict[randweap][0]['displayProperties']['icon'])
    
    return response


def get_lost_sectors():
    """
    Updated for Season 23 (now drops world drop weapons)
    """

    r = requests.get("https://www.todayindestiny.com/")
    soup = BeautifulSoup(r.text, "html.parser")
    important = soup.find_all("div", id=lambda x: x and x.startswith("lost_sector"))

    sector = important[0].find_all(class_="eventCardHeaderName")[0].get_text()
    
    modifiers = []
    armors = []
    weapons = []

    
    collecting_modifiers = True
    for i, line in enumerate(important[0].find_all(class_="manifest_item_tooltip_name")):
    
        ln = line.get_text()
    
        if "master modifiers" in ln.lower():
            continue
    
        if sector.lower() in ln.lower():
            collecting_modifiers = False
            continue
            
        if collecting_modifiers is True:
            modifiers.append(ln)

        else:
            # bottom four are weapons
            if i < len(important[0].find_all(class_="manifest_item_tooltip_name")) - 4:
                armors.append(ln)
            else:
                weapons.append(ln)
        
    return sector, modifiers, armors, weapons

get_lost_sectors()


def get_closest_gun(message, args, client, all_data, weapon_dict):
    words = list(weapon_dict.keys())

    name = " ".join(args)

    closest = difflib.get_close_matches(name, words)

    if len(closest) == 0:
        closest = difflib.get_close_matches(name.upper(), words)

    return closest
