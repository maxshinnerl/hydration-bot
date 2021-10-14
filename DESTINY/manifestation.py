# get data from manifest
import os
import requests
import zipfile
import pickle
import json
import sqlite3

from DESTINY.basics import *
# NOTE: when running locally, will need to remove the DESTINY. from the above import


def get_manifest():
    """
    Download manifest using requests and store in local directory
    """

    mnfst = make_request("destiny2/manifest")
    manifest_url = "http://www.bungie.net"+mnfst.data['mobileWorldContentPaths']['en']
    r = requests.get(manifest_url)

    with open("MANZIP", "wb") as zp:
        zp.write(r.content)
    print("manifest download done", flush=True)


    if os.path.exists('Manifest.content'):
        os.remove('Manifest.content')

    with zipfile.ZipFile('MANZIP') as zp:
        name = zp.namelist()
        zp.extractall()

    os.rename(name[0], "Manifest.content")
    print("Unzipped", flush=True)


def build_dict():
    #connect to the manifest
    con = sqlite3.connect('Manifest.content')
    print('Connected', flush=True)
    #create a cursor object
    cur = con.cursor()
    
    table_list = get_table_list(cur)

    all_data = {}
    #for every table name in the dictionary
    for table_name in table_list:
        #get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print('Generating '+table_name+' dictionary....', flush=True)

        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        #create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]

        #create a dictionary with the hashes as keys
        #and the jsons as values
        item_dict = {}
        #hash = hash_dict[table_name]
        try:
            for item in item_jsons:
                item_dict[item["hash"]] = item
                
        except KeyError:
            # for some reason this table uses "statId" not "hash"
            # too lazy to hard code for one edge case so we'll do this
            if table_name == "DestinyHistoricalStatsDefinition":
                for item in item_jsons:
                    item_dict[item["statId"]] = item
            
            else:
                print("Table has no hash and also is not HistoricalStats -max", flush=True)

        #add that dictionary to our all_data using the name of the table
        #as a key.
        all_data[table_name] = item_dict

    print('Dictionary Generated!')
    return all_data

def get_table_list(cur):
    """
    Replacement for hash_dict since I believe it may be irrelevant
    Just a list of all tables
    """
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tbls = [tbl[0] for tbl in cur.fetchall()] # get list of tables
    return tbls


def get_all_data(regen=False):
    """
    Pickle the output of build_dict.
    This function gives the all_data dict that should be used for everything
    """

    #check if pickle exists, if not create one.
    if regen == True:
        print("Regenerating manifest...", flush=True)
        get_manifest() 
        all_data = build_dict()
        with open('manifest.pickle', 'wb') as data:
            pickle.dump(all_data, data)
            print("'manifest.pickle' created!\nDONE!", flush=True)
    else:
        print("Not regenerating manifest")

    if os.path.isfile('manifest.pickle'):
        pass
    else:
        print("FAIL: Pickle not present.  Please set regen=True or import otherwise")

    with open('manifest.pickle', 'rb') as data:
        all_data = pickle.load(data)

    return all_data # the big'un


def get_weapon_buckets(all_data):
    """
    Get bucket hashes only for weapons
    output is dict of length 3 of format {buckethash, name}
    i.e. {123456: "energy weapons"}

    Needed for constructing the weapon_dict
    """
    weapon_buckets = {} # lets do {buckethash, name} as the format
    for item in list(all_data['DestinyInventoryBucketDefinition'].items()):
        if "name" in item[1]['displayProperties'].keys():
            if "weapon" in item[1]['displayProperties']['name'].lower():
                weapon_buckets[item[0]] = item[1]['displayProperties']['name']

    return weapon_buckets


def get_weapon_dict(all_data):
    """
    From all_data, extract information only for weapons.
    The format of this dictionary should be in the format:
        weapon_name : list of matches for that weapon name

    Reason for multiples: sunset and non-sunset are listed separately
    Also things like Aachen-LR2, where it exists as Kinetic and Energy

    NOTE: all_data is returned from get_all_data().  Do NOT call it within here: wasteful.
    Call it before and pass it in.  Ideally all_data (which downloads and updates manifest)
    is only called *once*.
    """

    weapon_buckets = get_weapon_buckets(all_data)

    weapons_dict = {}
    for item in list(all_data['DestinyInventoryItemDefinition'].items()):
    
        # check if weapon and 'quality' (used for checking light level) is available
        if (item[1]['inventory']['bucketTypeHash'] in weapon_buckets.keys()) and ('quality' in item[1].keys()):
            name = item[1]['displayProperties']['name']
        
            # if not yet in weapons_dict:
            if name not in weapons_dict.keys():
                weapons_dict[name] = []
            weapons_dict[name].append(item[1])

    # sort by the power level cap of weapon, so most recent version of weapon is presented first.
    for key, val in weapons_dict.items():
        weapons_dict[key] = sorted(val, key = lambda x: all_data['DestinyPowerCapDefinition'][x['quality']['versions'][0]['powerCapHash']]['powerCap'], reverse=True)

    return weapons_dict
