import discord
import os
from dotenv import load_dotenv

from api_keys import *

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

    print(message, flush=True)

    # in case your bot is the one saying the thing, just prevent endless recursion
    if message.author == client.user:
        return

    if message.content.lower() == 'matt is stinky':
        response = "super stinky, take a shower stinky.  Also drink water"
        await message.channel.send(response)
    

client.run(TOKEN)
