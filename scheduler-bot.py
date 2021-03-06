import json
import logger
import os
import random

from datetime import date
from dotenv import load_dotenv
from sys import exit

import discord
from discord.ext import commands, tasks
from discord.utils import get


log = logger.setup_applevel_logger(file_name = 'app_debug.log')


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('SCHEDULER_CHANNEL')
CAPTAINS = os.getenv('CAPTAINS')

with open('POLL_OPTIONS', 'r') as f:
    POLL_OPTIONS = eval(f.read())

RIDES = list(POLL_OPTIONS.values())
SCHEDULE = dict((ride, []) for ride in RIDES)
CAPTAINS_PER_RIDE = zip(RIDES, [1, 1, 2, 1, 1])

SCHEDULER_MSG = "@channel I'm a level 1 naive scheduling bot, and I make mistakes. " +\
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

    for ride, n_cap in CAPTAINS_PER_RIDE:
        log.debug('Calling {} on channel for {}.'.
            format(create_ride_schedule.__name__, ride))
        captains = await create_ride_schedule(ride, n_cap, avail)
        SCHEDULE[ride] = captains


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
    emojis = list(POLL_OPTIONS.keys())
    avail = dict((ride, []) for ride in RIDES)
    for reaction in reactions:
        ride_index = ''
        try:
            ride_index = emojis.index(reaction.emoji)
        except ValueError:
            log.error("Invalid reaction found: " + reaction.emoji)
            continue

        users = await reaction.users().flatten()
        for user in users:
            if not user.bot:
                avail[RIDES[ride_index]].append(user)
    
    log.debug('Availability is: {}'.format(
        "\n".join(f'{k}: {users_to_names(v)}' for k,v in avail.items())
    ))
    return avail


async def create_ride_schedule(ride, n_cap, avail):
    """Create road captain schedule
    """
    log.debug('Running {}.'.format(create_ride_schedule.__name__))
    await bot.wait_until_ready()

    log.debug('Choosing road captains for {}'.format(ride))
    captains = []
    
    # choose randomly for now
    for i in range(n_cap):

        #captain = prioritise_absence(ride, avail)

        try:
            captain = random.choice(avail[ride])
        except IndexError:
            captain = None

        captains.append(captain)

        # don't pick same captain twice for one ride
        if captain in avail[ride]:
            avail[ride].remove(captain)

        for s in avail.keys():
            if captain in avail[s] and len(avail[s]) > 2:
                log.debug('Scheduled {} on {}. Removing them from {}'.
                    format(captain.display_name, ride, s))
                avail[s].remove(captain)

    log.debug(
        "Road captains for {} are {}".format(ride, users_to_names(captains))
    )
    return captains


def prioritise_absence(ride, avail):
    """Prioritise captains that have been absent longer than others
    """
    log.debug('Running {}.'.format(prioritise_absence.__name__))


    with open('schedule') as f:
        schedule = [json.loads(line) for line in f]
    
    print(schedule)

    exit()
    return None


def update_logs():
    """Update log files.
    """
    log.debug('Running {}.'.format(update_logs.__name__))

    # log schedule to file
    log.debug('Saving schedule to log.')

    printable_schedule = SCHEDULE.copy()
    for ride in printable_schedule:
        printable_schedule[ride] = users_to_names(printable_schedule[ride])
    printable_schedule['date'] = str(date.today())

    json_schedule = json.dumps(printable_schedule)
    with open("schedule", 'a') as f:
        f.write('\n' + json_schedule)
    log.debug(json_schedule)


async def post_schedule(channel):
    """Post schedule to channel.
    """
    log.debug('Running {}.'.format(create_ride_schedule.__name__))
    await bot.wait_until_ready()

    msg = SCHEDULER_MSG + "\nRoad captains for this week are"

    schedule_post = SCHEDULE.copy()
    for ride in schedule_post:
        schedule_post[ride] = users_to_tags(schedule_post[ride])

    for k, v in schedule_post.items():
        msg += f"\n\n**{k}**\n" +\
                "\n".join(f'{c}' for c in v)

    log.debug('Send message to channel: \n{}'.format(msg))
    m = await channel.send(msg)


def users_to_names(users):
    """Convert a list of Users to a list of user names (str).
    """
    return [u.display_name if u is not None else '' for u in users]


def users_to_tags(users):
    """Convert a list of Users to a list of tags (str).
    """
    return ["<@!{}>".format(u.id) if u is not None else '' for u in users]


def user_to_tag(user):
    """Convert a list of Users to a list of tags (str).
    """
    return "<@!{}>".format(user.id) if user is not None else ''


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