# Lowest level hydration bot functions file, specifically for DESTINY stuff
import json

def weapstat(message, args, client, all_data, weapon_dict):
    """
    Get weapon stats for given weapon
    """

    weapon_name = " ".join(args)
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

    # no need for return arguments, just need to format the output
    response = ""
    for name, val in list(stats.items()):
        response += name + ": " + str(val) + "\n"

    return response
