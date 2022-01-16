import discord
from cmd_functions import *
from DESTINY import hbfunc

def command_handler(message, client, admin, all_data={}, weapon_dict={}, perk_dict={}):
    """
    called from on_message() in the main script
    """
    command, args = split_args(message)


    # lengthy decision tree, call different functions based on the command

    response = None
    ret_args = None

    if command == '$flirt':
        response = flirt(message, args)

    if command == '$move':
        if admin is True:
            response, ret_args = move(message, args, client)
        else:
            response = "Must be OTRN to use $move"

    if command == '$joinleave':
        response, ret_args = joinleave(message, args, client)

    if command == '$weapstat':
        response = hbfunc.weapstat(message, args, client, all_data, weapon_dict)

    if command == '$recoil':
        response = hbfunc.recoil(message, args, client, all_data, weapon_dict)

    if command == '$help':
        response = command_list(message, args, client)

    if command == '$usage':
        response = usage(message, args, client)
    
    if command == '$compare':
        response = hbfunc.compare(message, args, client, all_data, weapon_dict)

    if command == '$sametype':
        response = hbfunc.sametype(message, args, client, all_data, weapon_dict)

    if command == '$insult':
        response = insult(message, args)

    if command == '$perk':
        response = hbfunc.perk(message, args, client, all_data, perk_dict)

    if command == '$rolls':
        response = hbfunc.rolls(message, args, client, all_data, weapon_dict)

    if command == '$engram':
        response = hbfunc.engram(all_data, weapon_dict)
    
    if command == '$suggest':
        response = suggest(message, args)

    if command == '$suggestions':
        response = suggestions()

    if command == '$our':
        our(args)

    # messages need to be sent in an async function, do that in main
    return command, response, ret_args
     

def split_args(message):
    """
    take in message, output args as list
    """

    arg_list = message.content.split(' ')

    command = arg_list[0]
    args = arg_list[1:]

    return command, args


