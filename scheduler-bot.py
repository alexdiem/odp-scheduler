import os
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks
from discord.utils import get


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('SCHEDULER_CHANNEL')

# Define poll
POLL_TITLE = "Which days can you captain next week?"
POLL_EMOJIS = ['1️⃣', '2️⃣', '3️⃣']
POLL_OPTIONS = [
        POLL_EMOJIS[0] + " Tuesday", 
        POLL_EMOJIS[1] + " Wednesday", 
        POLL_EMOJIS[2] + " Thursday"
    ]
POLL_MESSAGE = POLL_TITLE + "\n\n" + "\n".join(POLL_OPTIONS)

# Instantiate bot
bot = commands.Bot(command_prefix='!')

async def send_poll(channel):
    """Send poll message to channel and add poll reactions 
    """
    await bot.wait_until_ready()
    m = await channel.send(POLL_MESSAGE)

    for emoji in POLL_EMOJIS:
        await m.add_reaction(emoji=emoji)

@bot.event
async def on_ready():
    """Set up variables and logging
    """
    await bot.wait_until_ready()

    print("Logged in as:")
    print(bot.user.name)
    print("------")

    channel = bot.get_channel(int(CHANNEL))
    print("Channel is:")
    print(channel)

    await send_poll(channel)


bot.run(TOKEN)