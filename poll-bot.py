import os
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks
from discord.utils import get

import logger
log = logger.setup_applevel_logger(file_name = 'app_debug.log')


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('SCHEDULER_CHANNEL')

# Define poll
POLL_TITLE = "Which days can you captain next week? The poll is open until midnight"
with open('POLL_OPTIONS', 'r') as f:
    POLL_OPTIONS = eval(f.read())
POLL_MESSAGE = POLL_TITLE +\
    "\n\n" + "\n".join(f'{k}: {v}' for k,v in POLL_OPTIONS.items())

# Instantiate bot
bot = commands.Bot(command_prefix='!')

async def send_poll(channel):
    """Send poll message to channel and add poll reactions 
    """
    log.debug('Running {}.'.format(send_poll.__name__))
    await bot.wait_until_ready()

    log.debug('Send message to channel: \n{}'.format(POLL_MESSAGE))
    m = await channel.send(POLL_MESSAGE)

    mid = m.id
    log.debug('Save message ID to file: \n{}'.format(mid))
    with open("MESSAGE_ID", 'w') as f:
        f.write(str(mid))

    for emoji in POLL_OPTIONS.keys():
        log.debug('Add reaction to poll: {}'.format(emoji))
        await m.add_reaction(emoji=emoji)

@bot.event
async def on_ready():
    """Set up variables and logging
    """
    log.debug('Running {}'.format(on_ready.__name__))
    await bot.wait_until_ready()

    log.debug('Logged in as {}'.format(bot.user.name))

    channel = bot.get_channel(int(CHANNEL))
    log.debug('Channel is {}'.format(channel))

    log.debug('Calling {} on channel.'.format(send_poll.__name__))
    await send_poll(channel)

    log.debug('Shutdown poll bot.')
    await bot.close()


log.debug('Starting poll bot.')
bot.run(TOKEN)