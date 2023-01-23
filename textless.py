# for messages without text, but present attachments

import discord
from junk import fashion
import numpy as np
import random

def process(message):
    print("PROCESSING", flush=True)
    response = None

    if str(message.channel).isin(["fashion", "purgatory"]):
        fashion_response = fashion.get_fashion()
        response = random.choice(fashion_response)




    return response

