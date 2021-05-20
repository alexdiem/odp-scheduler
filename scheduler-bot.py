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

POLL_EMOJIS = {'1️⃣': 'Tuesday', '2️⃣': 'Wednesday', '3️⃣': 'Thursday'}

# Instantiate bot
bot = commands.Bot(command_prefix='!')

async def read_poll_reactions(channel, msg_id):
    """Read reactions on last poll message 
    """
    log.debug('Running {}.'.format(read_poll_reactions.__name__))
    await bot.wait_until_ready()

    msg = await channel.fetch_message(msg_id)
    log.debug("Got message with ID {}".format(msg_id))
        
    reactions = msg.reactions

    log.debug('Calling {} on channel.'.format(create_schedule.__name__))
    await create_schedule(reactions)


async def create_schedule(reactions):
    """Create road captain schedule from reactions
    """
    log.debug('Running {}.'.format(create_schedule.__name__))
    await bot.wait_until_ready()

    log.debug('Getting availability from poll.')
    emojis = list(POLL_EMOJIS.keys())
    days = list(POLL_EMOJIS.values())
    avail = {days[0]: [], days[1]: [], days[2]: []}
    for reaction in reactions:
        day_index = emojis.index(reaction.emoji)
        users = await reaction.users().flatten()
        for user in users:
            if not user.bot:
                avail[days[day_index]].append(user.display_name)
    
    log.debug('Availability is: {}'.format(avail))


        



@bot.event
async def on_ready():
    """Set up variables and logging
    """
    log.debug('Running {}'.format(on_ready.__name__))
    await bot.wait_until_ready()

    log.debug('Logged in as {}'.format(bot.user.name))

    channel = bot.get_channel(int(CHANNEL))
    log.debug('Channel is {}'.format(channel))


    with open("MESSAGE_ID", 'r') as f:
        msg_id = int(f.readline())
    log.debug('Read poll message with ID {}.'.format(msg_id))

    log.debug('Calling {} on channel.'.format(read_poll_reactions.__name__))
    await read_poll_reactions(channel, msg_id)

    log.debug('Shutdown poll bot.')
    await bot.close()


log.debug('Starting scheduler bot.')
bot.run(TOKEN)