import random

from junk.flirts import *
from junk.insults import *
from junk.meme import Meme
from hard_coded.voice_channel_ids import *
from sklearn.model_selection import train_test_split
from junk.eightball import *
from junk.mc import parse_mc_question

import numpy as np
import pandas as pd
import datetime
import requests
from PIL import Image

"""
File for all functions relating to commands

Must be called from command_handling.py --> handle_command()
"""

def flirt(message, args):
    """
    Kind of a hello world, for @ing other people
    """
    if len(args) != 1:
        return

    if args[0][1] != '@':
        return

    else:
        # potentially choose a random response from a set
        flirts = get_flirts(str(message.author)[:-2], args[0])
        
        response = random.choice(flirts)

    return response


def insult(message, args, rebound=False):
    """
    They made me code this one ok

    Rebound is True if insult is being called as a result from a different command
    - in which case HBOt should insult the message author
    """

    if rebound is True:
        print(message.author)
        insults = get_insults("HydrationBot", str(message.author)[:-2])
        response = random.choice(insults)
        return response

    if len(args) != 1:
        return

    if args[0][1] != '@':
        return

    else:
        insults = get_insults(str(message.author)[:-2], args[0])
        response = random.choice(insults)

    return response


def move(message, args, client):
    """
    Move all users from one channel to another

    origin channel is first arg, receiving channel is second arg
    """

    origin_channel =      vcs[args[0].lower()]
    destination_channel = vcs[args[1].lower()]

    origin_channel = client.get_channel(int(origin_channel[2:][:-1]))
    destination_channel = client.get_channel(int(destination_channel[2:][:-1]))

    member_ids = list(origin_channel.voice_states.keys())#[member.id for member in origin_channel.members]

    ret_args = member_ids.copy()
    ret_args.append(destination_channel)

    response = f"Moving channel {args[0]} to {args[1]}"

    return response, ret_args


def joinleave(message, args, client):
    """
    Join and leave specified channel (args[0])
    Just testing here
    """
    origin_channel =      vcs[args[0].lower()]
    origin_channel = client.get_channel(int(origin_channel[2:][:-1]))

    response = f"joining and leaving {args[0]}"

    ret_args = []
    ret_args.append(origin_channel)
    return response, ret_args


def split_teams(client):
    """
    Split people in waiting-room into teams and move to alpha/bravo
    """
    waiting_room = client.get_channel(957378114189664266) # Waiting-Room
    alpha_channel = client.get_channel(957378187850035201) # Alpha
    bravo_channel = client.get_channel(957378227960168499) # Bravo

    member_ids = list(waiting_room.voice_states.keys())

    alpha_team, bravo_team = train_test_split(member_ids, train_size=0.5)
 
    ret_args = {}
    ret_args["waiting_room"]  = waiting_room
    ret_args["alpha_channel"] = alpha_channel
    ret_args["bravo_channel"] = bravo_channel
    ret_args["alpha_team"]    = alpha_team
    ret_args["bravo_team"]    = bravo_team

    return ret_args


def finish_game(client):
    """
    Move people back into waiting room
    """
    waiting_room = client.get_channel(957378114189664266) # Waiting-Room
    alpha_channel = client.get_channel(957378187850035201) # Alpha
    bravo_channel = client.get_channel(957378227960168499) # Bravo

    alpha_ids = list(alpha_channel.voice_states.keys())
    bravo_ids = list(bravo_channel.voice_states.keys())
    member_ids = alpha_ids + bravo_ids

    ret_args = {}
    ret_args["waiting_room"]  = waiting_room
    ret_args["memberids"]     = member_ids
    
    return ret_args


def command_list(message, args, client):
    """
    corresponding to $help command

    Just list current available commands
    """

    with open("junk/help.txt") as f:
        response = f.read()

    return response
    

def usage(message, args, client):
    """

    """
    if len(args) != 1:
        return "Incorrect usage call, try $usage <command>\nExample:\n$usage $flirt"

    # command in question
    ciq = args[0]
    if ciq[0] == "$":
        ciq = ciq[1:]

    # load in file
    # NOTE: maintain usage directory, with corresponding instruction file as cmd.txt

    with open(f"usage/{ciq}.txt") as f:
        response = f.read()

    return response


def suggest(message, args):
    """
    Take in a suggestion, append it to the SUGGESTIONS/suggest.txt file.
    """

    author = message.author.name
    print(author, flush=True)

    if len(args) > 0:
        response = "Added to suggestion box (not a paper shredder)"
    else:
        return "No suggestion detected.  Be better."

    suggestion = " ".join(args)
    with open("SUGGESTIONS/suggestion.txt", "a") as f:
        f.write("(" + author + ") -- " + suggestion + "\n\n")

    return response


def suggestions():
    """
    Print out current suggestions to discord.
    """
    with open("SUGGESTIONS/suggestion.txt", "r") as f:
        response = f.read()

    return response


def names(message, args):
    """
    Take in a name, append it to the SUGGESTIONS/names.txt file.
    """
    name = " ".join(args)

    author = message.author.name
    print(author, flush=True)

    if len(args) ==  0:
        with open("SUGGESTIONS/names.txt", "r") as f:
            response = f.read()

        if len(response) == 0:
            response = "No names on file"

        return response

    response = f"Added name: {name}"

    with open("SUGGESTIONS/names.txt", "a") as f:
        f.write(name + " -- (" + author + ")" + "\n\n")

    return response


def meme(cmd, text):
    """
    Text is to be added to image
    """
    meme = Meme(cmd)
    meme.make_image(text)


def eightball():
    """
    Random 8ball response

    They made me code this one ok
    """
    eightballs = get_eightball_response()
    response = random.choice(eightballs)

    return response


def randno(maximum):
    """
    Given maximum, give random number from 1 to maximum
    """
    return np.random.randint(maximum) + 1


def mc(question: str):
    """Multiple choice questions."""
    response = parse_mc_question(" ".join(question))
    if not response:
        return "Could not find a choice. use a) choice1 b) choice2 c) choice 3."
    return response


def twab():
    cur = datetime.datetime.now().date()
    while cur.weekday() != 3:
        cur -= datetime.timedelta(days=1)
    
    y = str(cur)[:4]
    m = str(cur)[5:7]
    d = str(cur)[-2:]

    url = f"https://www.bungie.net/7/en/News/article/this_week_in_destiny_{m}_{d}_{y}"

    if requests.get(url).status_code == 200:
        return url

    return f"No twab for most recent thursday ({m}-{d}-{y})"


def get_fusion():
    
    code = 404
    while code != 200:
    
        head = np.random.randint(470) + 1
        body = np.random.randint(470) + 1
    
        url = f"http://if.daena.me/{head}.{body}"
    
        r = requests.get(url)
        code = r.status_code
    
    # text processing
    name = r.text.split("title")[1].split(" #")[0][1:]
    r = pd.Series(r.text.split(" "))
    s = r[r.str.contains("png")].reset_index().iloc[0].values[1]
    s = s[9:-8]
    
    response = requests.get(s)
    if response.status_code == 200:
        with open("images/fusion.png", 'wb') as f:
            f.write(response.content)
    else:
        return f"request failed for head {head} and body {body}"
    
    return name
