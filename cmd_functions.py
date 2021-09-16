import discord
import numpy as np
import random

from junk.flirts import *
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
