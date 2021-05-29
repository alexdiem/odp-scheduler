import os
from sys import exit
from dotenv import load_dotenv
import random
from datetime import date

import discord
from discord.ext import commands, tasks
from discord.utils import get

import logger
log = logger.setup_applevel_logger(file_name = 'app_debug.log')


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('SCHEDULER_CHANNEL')

DAYS = ['Tuesday', 'Wednesday', 'Thursday']
SCHEDULE = {DAYS[0]: [], DAYS[1]: [], DAYS[2]: []}
CAPTAINS_PER_DAY = 2

POLL_EMOJIS = {'1️⃣': DAYS[0], '2️⃣': DAYS[1], '3️⃣': DAYS[2]}

SCHEDULER_MSG = "I'm a level 1 naive scheduling bot, and I make mistakes. " +\
    "<@!766548029116907570> will help me fix it.\n"

# Instantiate bot
bot = commands.Bot(command_prefix='!')

async def manage_schedule(channel, msg_id):
    """Read reactions on last poll message 
    """
    log.debug('Running {}.'.format(manage_schedule.__name__))
    await bot.wait_until_ready()

    try:
        msg = await channel.fetch_message(msg_id)
    except discord.errors.NotFound:
        log.error("Discord error: Message ID {} not found.".format(msg_id))
        await bot.close()
        exit()
        
    log.debug("Got message with ID {}".format(msg_id))
        
    reactions = msg.reactions

    log.debug('Calling {} on channel.'.format(read_reactions.__name__))
    avail = await read_reactions(reactions)

    days = POLL_EMOJIS.values()
    schedule = []
    for day in days:
        log.debug('Calling {} on channel for {}.'.
            format(create_day_schedule.__name__, day))
        captains = await create_day_schedule(day, avail)
        SCHEDULE[day] = captains

    log.debug('Calling {}.'.format(update_logs.__name__))
    update_logs()

    log.debug('Calling {} on channel.'.format(post_schedule.__name__))
    await post_schedule(channel)


async def read_reactions(reactions):
    """Read reactions from scheduler poll
    """
    log.debug('Running {}.'.format(read_reactions.__name__))
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
                avail[days[day_index]].append(user)
    
    log.debug('Availability is: {}'.format(avail))
    return avail


async def create_day_schedule(day, avail):
    """Create road captain schedule
    """
    log.debug('Running {}.'.format(create_day_schedule.__name__))
    await bot.wait_until_ready()

    log.debug('Choosing road captains for {}'.format(day))
    captains = []
    
    # choose randomly for now
    for i in range(CAPTAINS_PER_DAY):
        try:
            captain = random.choice(avail[day])
        except IndexError:
            captain = None

        captains.append(captain)

        # don't pick same captain twice for one day
        if captain in avail[day]:
            avail[day].remove(captain)

        for s in avail.keys():
            if captain in avail[s] and len(avail[s]) > 2:
                log.debug('Scheduled {} on {}. Removing them from {}'.
                    format(captain.display_name, day, s))
                avail[s].remove(captain)

    log.debug(
        "Road captains for {} are {}".format(day, users_to_names(captains))
    )
    return captains


def update_logs():
    """Update log files.
    """
    log.debug('Running {}.'.format(update_logs.__name__))

    # log schedule to file
    log.debug('Saving schedule to log.')
    schedule_log = "{},{},{},{}\n".format(
            date.today(), 
            users_to_names(SCHEDULE[DAYS[0]]), 
            users_to_names(SCHEDULE[DAYS[1]]), 
            users_to_names(SCHEDULE[DAYS[2]])
            )
    with open("schedule", 'a') as f:
        f.write(schedule_log)
    log.debug(schedule_log)


async def post_schedule(channel):
    """Post schedule to channel.
    """
    log.debug('Running {}.'.format(create_day_schedule.__name__))
    await bot.wait_until_ready()

    msg = SCHEDULER_MSG +\
        "Road captains for Tuesday are {}>.\n".format(
            users_to_tags(SCHEDULE[DAYS[0]])
            ) +\
        "Road captains for Wednesday are {}.\n".format(
            users_to_tags(SCHEDULE[DAYS[1]])
            ) +\
        "Road captains for Thursday are {}.\n".format(
            users_to_tags(SCHEDULE[DAYS[2]])
            )

    log.debug('Send message to channel: \n{}'.format(msg))
    #m = await channel.send(msg)


def users_to_names(users):
    """Convert a list of Users to a list of user names (str).
    """
    return [u.display_name if u is not None else '' for u in users]


def users_to_tags(users):
    """Convert a list of Users to a list of tags (str).
    """
    return ["<@!{}>".format(u.id) if u is not None else '' for u in users]


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

    log.debug('Calling {} on channel.'.format(manage_schedule.__name__))
    await manage_schedule(channel, msg_id)

    log.debug('Shutdown poll bot.')
    await bot.close()


log.debug('Starting scheduler bot.')
bot.run(TOKEN)