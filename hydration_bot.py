import discord
import os
from dotenv import load_dotenv
import numpy as np

from api_keys import *
from command_handling import *

from DESTINY import basics
from DESTINY import manifestation

load_dotenv()

# from api_keys.py
TOKEN = HB_KEY
GUILD = SERVER

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# so tldr just make functions like on_ready, on_message, etc
# add the @client.event tag (decorator?) before each one

# generate manifest
regen = input("Rebuild manifest? y/n (DO NOT RUN ON AWS): ")
if regen.lower() == "y":
    all_data = manifestation.get_all_data(regen=True)
elif regen.lower() == "n":
    all_data = manifestation.get_all_data(regen=False)
else:
    print("assuming no", flush=True)
    all_data = manifestaion.get_all_data(regen=False)

weapon_dict = manifestation.get_weapon_dict(all_data)
perk_dict = manifestation.get_perk_dict(all_data)


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
async def on_member_join(member):
    print("member joined:", member)
    role = discord.utils.get(member.guild.roles, name="LFG-Recruits")
    await member.add_roles(role)

    channel = discord.utils.get(member.guild.text_channels, name="general")
    member_mention = member.mention

    bot_channel = discord.utils.get(member.guild.text_channels, name="mute-this-bot-commands").mention
    me = discord.utils.get(member.guild.members, name="EatYoWaffles").mention

    with open("junk/welcome.txt") as f:
        text = f.read()

    welcome = text.format(**locals()) 

    await channel.send(welcome)


@client.event
async def on_message(message):
    """
    Handle messages

    Let's say commands starting with $ are commands for this bot.
    send that to message_handling.py
    """

    BAguild = client.guilds[0]

    response = None

    print("message received: ", message.author, flush=True)
    
    if len(message.content) == 0:
        return

    if message.author == client.user:
        return

    # get admin status
    if message.author.top_role.name == "OTRN":
        admin = True
    else:
        admin = False

    # in case your bot is the one saying the thing, just prevent endless recursion

    if message.content[0] == '$':
        # command
        command, response, args = command_handler(message,
                                                  client,
                                                  admin,
                                                  all_data=all_data,
                                                  weapon_dict=weapon_dict,
                                                  perk_dict=perk_dict)
        
        # execute stuff
        if (command == "$move") and (admin is True):
            for memberid in args[:-1]:
                member = await BAguild.fetch_member(memberid)
                await member.move_to(args[-1])
   

        elif command == "$joinleave":
            print('joinleave: ', args[0], flush=True)
            channel = args[0]
            await channel.connect()
            for clnt in client.voice_clients:
                # NOTE: might need to add a checker here in case bot is present in multiple channels
                print(clnt, flush=True)
                await clnt.disconnect()

        elif command == "$compare":

            if response == "Generated":
                # we have a result
                await message.channel.send(file=discord.File('images/comp.png'))
                response = None

        elif command == "$sausage":

            num_sosig = 5 
            sosig = np.random.randint(num_sosig)

            await message.channel.send(file=discord.File(f'images/sausage{sosig}.jpg'))
            response = None



    # Hello world example
    if message.content.lower() == 'matt is stinky':
        response = "super stinky, take a shower stinky.  Also drink water"

    if (":o" in message.content.lower()) or ("😮" in message.content.lower()):
        rndm = np.random.randint(10)
        if rndm == 0:
            response = "omg he's doing the pog face XDDDDDDDD"


    if response is not None:    
        await message.channel.send(response)


client.run(TOKEN)
