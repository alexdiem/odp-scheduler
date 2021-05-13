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

# Instantiate bot
bot = commands.Bot(command_prefix='!')

async def read_poll_reactions(msg_id):
    """Read reactions on last poll message 
    """
    log.debug('Running {}.'.format(read_poll_reactions.__name__))
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    """Set up variables and logging
    """
    log.debug('Running {}'.format(on_ready.__name__))
    await bot.wait_until_ready()

    log.debug('Logged in as {}'.format(bot.user.name))

    channel = bot.get_channel(int(CHANNEL))
    log.debug('Channel is {}'.format(channel))

    log.debug('Read poll message ID.')
    with open("MESSAGE_ID", 'r') as f:
        msg_id = int(f.readline())

    log.debug('Calling {} on channel.'.format(read_poll_reactions.__name__))
    await read_poll_reactions(msg_id)

    log.debug('Shutdown poll bot.')
    await bot.close()


log.debug('Starting scheduler bot.')
bot.run(TOKEN)