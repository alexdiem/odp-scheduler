import os
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks
from discord.utils import get


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('SCHEDULER_CHANNEL')

POLL_TITLE = "Which days can you captain next week?"
POLL_EMOJIS = ['1️⃣', '2️⃣', '3️⃣']
POLL_OPTIONS = [
        POLL_EMOJIS[0] + " Tuesday", 
        POLL_EMOJIS[1] + " Wednesday", 
        POLL_EMOJIS[2] + " Thursday"
    ]
POLL_MESSAGE = POLL_TITLE + "\n\n" + "\n".join(POLL_OPTIONS)


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print("Logged in as:")
    print(bot.user.name)
    print("------")
    channel = bot.get_channel(int(CHANNEL))
    print("Channel is:")
    print(channel) #Prints None
    poll.start(channel)


@tasks.loop(seconds=5.0, count=1)
async def poll(channel):
    await bot.wait_until_ready()
    m = await channel.send(POLL_MESSAGE)

    for emoji in POLL_EMOJIS:
        await m.add_reaction(emoji=emoji)


bot.run(TOKEN)