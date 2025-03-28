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

    if command == '$hydrate':
        response, ret_args = joinleave(message, args, client)
        response = str(args[0]) + " is now hydrated."

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

        if len(response.split("\n")) < 5: # rolls dict was empty
            response = response.replace("See the $perk command for details on any of the above", "*This weapon has set rolls.*")

    if command == '$engram':
        response = hbfunc.engram(all_data, weapon_dict)
    
    if command == '$suggest':
        response = suggest(message, args)

    if command == '$suggestions':
        response = suggestions()

    if command == '$names':
        response = names(message, args)

    if command == '$our':
        meme('our', args)

    if command == '$no':
        meme('no', args)

    if command == '$split':
        ret_args = split_teams(client)
        response = "Splitting teams..."

    if command == '$finish':
        ret_args = finish_game(client)
        response = "Bringing everyone back..."

    if command == '$closest':
        ret_args = hbfunc.get_closest_gun(message, args, client, all_data, weapon_dict)
        if len(ret_args) == 0:
            response = "Not recognized"
        else:
            response = "**Found the following:**"
            for w in ret_args:
                response += "\n" + w

    if command == '$8ball':
        response = eightball()

    if command == '$randno':
        response = randno(args[0])

    if command == "$mc":
        response = mc(args)

    if command == '$combo':
        response = hbfunc.combo(args, all_data, weapon_dict, perk_dict)
        if response == -1:
            response = insult(message, args, rebound=True)

    if command == '$clear':
        response = "CLEAR\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nType something..."

    if command == '$twab':
        response = twab()

    if command == '$fusion':
        response = get_fusion()


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
