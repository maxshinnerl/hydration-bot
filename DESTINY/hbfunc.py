# Lowest level hydration bot functions file, specifically for DESTINY stuff
import json
import numpy as np
import matplotlib.pyplot as plt

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

    return stats

def weapstat(message, args, client, all_data, weapon_dict):
    """
    Get weapon stats for given weapon
    """

    weapon_name = " ".join(args)
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

    weapon_name = " ".join(args)
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

    w1_stats = get_weapon_stats(w1, all_data, weapon_dict)
    w2_stats = get_weapon_stats(w2, all_data, weapon_dict)
    
    if w1_stats.keys() != w2_stats.keys():
        response = "Weapons too different to compare"
        return response
    
    labels = list(w1_stats.keys())[2:]
    
    w1_values = list(w1_stats.values())[2:]
    w2_values = list(w2_stats.values())[2:]
    
    x = np.arange(len(labels)) * 2
    width = 0.7
    
    fig, ax = plt.subplots(figsize=(10,6))
    rects1 = ax.barh(x - width/2, w1_values, width, align='edge', label=w1)
    rects2 = ax.barh(x + width/2, w2_values, width, align='edge', label=w2)
    
    ax.set_title('Stat Comparison of ' + w1 + ' and ' + w2)
    ax.set_yticks(x)
    ax.set_yticklabels(labels)
    ax.legend()

    # ax.text(x,y,string)
    
    for rect1, rect2 in zip(rects1, rects2):
        ax.text(rect1.get_width(), rect1.get_y()+0.15, rect1.get_width())
        ax.text(rect2.get_width(), rect2.get_y()+0.15, rect2.get_width())
    
    fig.tight_layout()

    plt.savefig("images/comp.png")
    
    return "Generated"
    
