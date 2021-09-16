import discord
import os
from dotenv import load_dotenv

from api_keys import *
from command_handling import *

load_dotenv()

# from api_keys.py
TOKEN = HB_KEY
GUILD = SERVER

client = discord.Client()


# so tldr just make functions like on_ready, on_message, etc
# add the @client.event tag (decorator?) before each one

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!', flush=True)
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})',
        flush=True
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}', flush=True)


@client.event
async def on_message(message):
    """
    Handle messages

    Let's say commands starting with $ are commands for this bot.
    send that to message_handling.py
    """
    BAguild = client.guilds[0]
    #print("here", BAguild, type(BAguild), flush=True)


    response = None


    # in case your bot is the one saying the thing, just prevent endless recursion
    if message.author == client.user:
        return

    if message.content[0] == '$':
        # command
        command, response, args = command_handler(message, client)
        
        # execute stuff
        if command == "$move":
            for memberid in args[:-1]:
                member = await BAguild.fetch_member(memberid)
                await member.move_to(args[-1])

    # Hello world example
    if message.content.lower() == 'matt is stinky':
        response = "super stinky, take a shower stinky.  Also drink water"

    if response is not None:    
        await message.channel.send(response)


client.run(TOKEN)
