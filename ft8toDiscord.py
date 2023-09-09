# Pip install adif_io d discord.py pyhamtools  emoji-country-flag country_converter

import os
import flag
import adif_io
import discord
from discord.ext import commands, tasks
import asyncio
from pyhamtools.locator import *
import country_converter as coco
from pyhamtools import LookupLib, Callinfo

# File log to get ADIF lines from
LOGFILE="~/.local/share/JTDX/wsjtx_log.adi"

# *** REPLACE DISCORD_CHANNEL_ID WITH YOUR DISCORD CHANNEL ID ***
# id of the discord channel to send logs to
DiscordChannel = DISCORD_CHANNEL_ID

# *** REPLACE DISCORD_BOT_ID WITH YOUR BOT TOKEN ***
# The API Key of the bot
BotKEY = 'DISCORD_BOT_ID'

# expanduser is used to get the absolute path of the file
LOGFILE=os.path.expanduser(LOGFILE)
# we get the directory name of the file
LOGPATH = os.path.dirname(LOGFILE)
# Conversion db from HAM call to country
HAMdb = LookupLib(lookuptype="countryfile")


# Discord Bot initialization
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!',intents=intents)


def getCountryFlagFromName(name):
    countrySymbol = cc.convert(names = name, to = 'ISO2')
    countryFlag = flag.flag(countrySymbol)
    #country = name + " " + countryFlag
    #print( countrySymbol)
    return countryFlag

def extract_ADIF(entry):
    record=adif_io.read_from_string(entry)[0][0]
    # We get the info we need from the ADIF line
    call=record['CALL']
    locator=record['GRIDSQUARE']
    mode=record['MODE']
    mycall=record['STATION_CALLSIGN']
    mylocator=record['MY_GRIDSQUARE']
    rstsent=record['RST_SENT']
    rstrcvd=record['RST_RCVD']
    freq=record['FREQ']
    band=record['BAND']
    qsologged=record['QSO_DATE_OFF'] + " - " + record['TIME_OFF']
    country = cic.get_country_name(call)
    country = country + " " + getCountryFlagFromName(country)
    # We get the country flag so it's pretty :)
    distance = ''
    if locator != '':
        distance =  str(int(calculate_distance(mylocator,locator)))
    # We compose our message
    message = "> **" + mycall + "**: new contact - " + mode + " -- *" + distance + " km* \n"
    message+= ">    With **" + call + "** ( " + locator + " // " + country + " ) \n"
    message+= ">    Freq.: **" + freq + " Mhz** (" + band + ") -- "
    message+= ">    RST Sent: " + rstsent + " RST Received: " + rstrcvd
    #message+= "\n~~                                                     ~~"
    message+="\n\n "
    # Back to Tim !
    return message

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await send_msg()

@client.event
async def send_msg():
    channel = client.get_channel(DiscordChannel)
#    await channel.send('Bot FT8 Connected')
    # We get an eye on the logfile to extract a new line
    with open(LOGFILE, 'r') as file:
    # We go to the end of file to catch new lines
        file.seek(0, 2)
        while True:
            line = file.readline()
            if line:
                entry = line.strip()
                print("new line:", entry)
                discord_msg = extract_ADIF(entry)
                await channel.send(discord_msg)

            else:
                # If no new line, we go to another turn
                await asyncio.sleep(1)

# We get the Country-HAM prefix db for conversions
cic = Callinfo(HAMdb)
# coco is needed in order to convert country name into its 2 char symbol
cc = coco.CountryConverter()
# The bot is launched
client.run(BotKEY)
