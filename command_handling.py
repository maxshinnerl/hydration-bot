import discord
from cmd_functions import *
from DESTINY import hbfunc

def command_handler(message, client, all_data, weapon_dict):
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
        response, ret_args = move(message, args, client)

    if command == '$joinleave':
        response, ret_args = joinleave(message, args, client)

    if command == '$weapstat':
        response = hbfunc.weapstat(message, args, client, all_data, weapon_dict)
    
    
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


