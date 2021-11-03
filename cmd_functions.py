import discord
import numpy as np
import random

from junk.flirts import *
from junk.insults import *
from hard_coded.voice_channel_ids import *

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
        flirts = get_flirts(str(message.author)[:-5], args[0])
        
        response = random.choice(flirts)

    return response


def insult(message, args):
    """
    They made me code this one ok
    """
    if len(args) != 1:
        return

    if args[0][1] != '@':
        return

    else:
        insults = get_insults(str(message.author)[:-5], args[0])
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


