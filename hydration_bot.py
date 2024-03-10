import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
import numpy as np
import datetime

from api_keys import *
from command_handling import *

from DESTINY import basics
from DESTINY import manifestation
from DESTINY.hbfunc import get_lost_sectors
from TWITTER import tweetie

import textless

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

BIRTHDAY = False

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


@tasks.loop(seconds = 60)
async def daily_reset_grab():
    now = datetime.datetime.now().time().strftime("%H:%M") 

    # set the time below to like 5 minutes after reset
    # may have to update after daylight savings
    # basically either 09:05 or 10:05 (leading zero needed)

    # NOTE: EC2 runs on GMT.  +8 hours.  At least we don't have to convert savings time?
    # Reset is at 17:00 GMT.   Adjust accordingly

    # Now with Pi:  09:05 should be correct (until daylight savings)

    if now == "10:05":

        print("it's time!", flush=True)
        
        # Let's also do lost sectors
        sector, modifiers, armors, weapons = get_lost_sectors()
        response = "**Lost Sector Today**\n" + sector + "\n\n"

        response += "**Modifiers**\n" + "\n".join(modifiers) + "\n\n"

        response += "**Armor**\n" + "\n".join(armors) + "\n\n"

        response += "**Weapons**\n" +  "\n".join(weapons) + "\n\n"

        response += "\nSource: Today in Destiny: https://www.todayindestiny.com/"

        channel = client.get_channel(853842181759434793) 
        await channel.send(response)


    # birthday
    m = datetime.datetime.now().month
    d = datetime.datetime.now().day
    y = datetime.datetime.now().year

    if (m == 8) and (d == 31):
        # check if you've announced birthday yet
        if BIRTHDAY is False:
            response = "It's my birthday, I am now" + str(y - 2021) + " years old."
            channel = client.get_channel(875160886585720884) # random
            await channel.send(response)
            BIRTHDAY=True

    if m == 9:
        BIRTHDAY = False


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
    
    if (len(message.content) == 0) and (len(message.attachments)==0):
            print("EMPTY", flush=True)
            return

    elif len(message.content) == 0:
        print("TEXTLESS ATTACHMENT")
        response = textless.process(message)
        if response is not None:    
            await message.channel.send(response)

        return


    # in case your bot is the one saying the thing, just prevent endless recursion
    if message.author == client.user:
        return

    # TODO make this role-based
    #if "tofutyranny" in str(message.author).lower():
    #    await message.channel.send("BOZO^")



    # get admin status
    if message.author.top_role.name == "OTRN":
        admin = True
    else:
        admin = False

    # clean message (for stinky mobile users)
    message.content = message.content.replace("‘", "'")
    message.content = message.content.replace("`", "'")
    message.content = message.content.replace("‘", "'")
    message.content = message.content.replace("'", "'")
    message.content = message.content.replace("’", "'")


    if message.content[0] == '$':

        # if long command, warn user
        command = message.content.split(" ")[0]
        if command in ["$combo"]:
            await message.channel.send(f"{command} call received, please wait a few seconds")
            

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

        
        elif (command == "$split") and (admin is True):
            # move alpha
            for memberid in args['alpha_team']:
                member = await BAguild.fetch_member(memberid)
                await member.move_to(args['alpha_channel'])

            # move bravo
            for memberid in args['bravo_team']:
                member = await BAguild.fetch_member(memberid)
                await member.move_to(args['bravo_channel'])

        elif (command == "$finish") and (admin is True):
            # move everyone back
            for memberid in args['memberids']:
                member = await BAguild.fetch_member(memberid)
                await member.move_to(args['waiting_room'])
            

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

        elif command == "$engram":
            await message.channel.send(file=discord.File(f'images/icon.png'))

        elif command == "$our":
            await message.channel.send(file=discord.File("junk/our_edited.jpg"))

    # Hello world example
    if message.content.lower() == 'matt is stinky':
        # await message.channel.send(file=discord.File("junk/shower.txt"))
        response = "NO.  Matt is POGGERS"

    if (":o" in message.content.lower()) or ("😮" in message.content.lower()):
        rndm = np.random.randint(10)
        if rndm == 0:
            response = "omg he's doing the pog face XDDDDDDDD"


    if is_sheesh(message.content.lower()) is True:
        response = "🥶"

    if ("i have a 5/5" in message.content.lower()) or ("i got a 5/5" in message.content.lower()):
        response = "kill yourself"

    if response is not None:    
        await message.channel.send(response)

daily_reset_grab.start()
client.run(TOKEN)
