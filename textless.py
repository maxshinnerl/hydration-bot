# for messages without text, but present attachments

import discord
from junk import fashion
import numpy as np
import random

def process(message):
    response = None

    if str(message.channel) == "fashion":
        fashion_response = fashion.get_fashion()
        response = random.choice(fashion_response)




    return response
