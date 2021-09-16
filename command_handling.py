import discord
from cmd_functions import *

def command_handler(message, client):
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


