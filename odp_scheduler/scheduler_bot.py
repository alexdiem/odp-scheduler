import discord
from discord.ext import commands

import json
import os
import random

from datetime import date, timedelta


class SchedulerBot(commands.Bot):

    def __init__(self, command_prefix, self_bot, options, db, log, debug=False):
        self.DEBUG = debug
        self.db = db
        self.LOG = log
        self.CHANNEL = os.getenv('SCHEDULER_CHANNEL')
        self.SCHEDULER_MSG = "@everyone I'm a level 1 naive scheduling bot, and I make mistakes. " +\
                "<@!766548029116907570> will help me fix it.\n"

        with open(options, 'r') as f:
            self.POLL_OPTIONS = eval(f.read())
        
        self.RIDES = list(self.POLL_OPTIONS.values())
        self.SCHEDULE = dict((ride, []) for ride in self.RIDES)
        self.CAPTAINS_PER_RIDE = zip(self.RIDES, [1, 1])

        # Instantiate bot
        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)


    async def manage_schedule(self, channel, msg_id):
        """Read reactions on last poll message 
        """
        self.log_debug('Running {}.'.format(self.manage_schedule.__name__))
        await self.wait_until_ready()

        try:
            msg = await channel.fetch_message(msg_id)
        except discord.errors.NotFound:
            self.log_debug("Discord error: Message ID {} not found.".format(msg_id))
            await self.close()
            exit()
            
        self.log_debug("Got message with ID {}".format(msg_id))
            
        reactions = msg.reactions

        self.log_debug('Calling {} on channel.'.format(self.read_reactions.__name__))
        avail = await self.read_reactions(reactions)

        for ride, n_cap in self.CAPTAINS_PER_RIDE:
            self.log_debug('Calling {} on channel for {}.'.
                format(self.create_ride_schedule.__name__, ride))
            captains = await self.create_ride_schedule(ride, n_cap, avail)
            self.SCHEDULE[ride] = captains


        self.log_debug('Calling {}.'.format(self.update_logs.__name__))
        self.update_logs()
        
        if not self.DEBUG:
            self.log_debug('Calling {} on channel.'.format(self.post_schedule.__name__))
            await self.post_schedule(channel)


    async def read_reactions(self, reactions):
        """Read reactions from scheduler poll
        """
        self.log_debug('Running {}.'.format(self.read_reactions.__name__))
        await self.wait_until_ready()

        self.log_debug('Getting availability from poll.')
        emojis = list(self.POLL_OPTIONS.keys())
        avail = dict((ride, []) for ride in self.RIDES)
        for reaction in reactions:
            ride_index = ''
            try:
                ride_index = emojis.index(reaction.emoji)
            except ValueError:
                self.log_error("Invalid reaction found: {}".format(reaction.emoji))
                continue

            users = [user async for user in reaction.users()]
            for user in users:
                if not user.bot:
                    avail[self.RIDES[ride_index]].append(user)
        
        self.log_debug('Availability is: {}'.format(
            "\n".join(f'{k}: {self.users_to_names(v)}' for k,v in avail.items())
        ))
        return avail


    async def create_ride_schedule(self, ride, n_cap, avail):
        """Create road captain schedule
        """
        self.log_debug('Running {}.'.format(self.create_ride_schedule.__name__))
        await self.wait_until_ready()

        self.log_debug('Choosing road captains for {}'.format(ride))
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
                    self.log_debug('Scheduled {} on {}. Removing them from {}'.
                        format(captain.display_name, ride, s))
                    avail[s].remove(captain)

        self.log_debug(
            "Road captains for {} are {}".format(ride, self.users_to_names(captains))
        )
        return captains


    def prioritise_absence(self, ride, avail):
        """Prioritise captains that have been absent longer than others. Not yet in use.
        """
        self.log_debug('Running {}.'.format(self.prioritise_absence.__name__))


        with open('schedule') as f:
            schedule = [json.loads(line) for line in f]
        
        print(schedule)


    def update_logs(self):
        """Update log files.
        """
        self.log_debug('Running {}.'.format(self.update_logs.__name__))

        # log schedule to file
        self.log_debug('Saving schedule to log.')

        printable_schedule = self.SCHEDULE.copy()
        for ride in printable_schedule:
            printable_schedule[ride] = self.users_to_names(printable_schedule[ride])
        printable_schedule['date'] = str(date.today())

        json_schedule = json.dumps(printable_schedule)
        self.log_debug(json_schedule)


    async def post_schedule(self, channel):
        """Post schedule to channel.
        """
        self.log_debug('Running {}.'.format(self.create_ride_schedule.__name__))
        await self.wait_until_ready()

        msg = self.SCHEDULER_MSG + "\nRoad captains for this week are"

        schedule_post = self.SCHEDULE.copy()
        for ride in schedule_post:
            schedule_post[ride] = self.users_to_tags(schedule_post[ride])

        for k, v in schedule_post.items():
            msg += f"\n\n**{k}**\n" +\
                    "\n".join(f'{c}' for c in v)

        self.log_debug('Send message to channel: \n{}'.format(msg))
        m = await channel.send(msg)


    def users_to_names(self, users):
        """Convert a list of Users to a list of user names (str).
        """
        return [u.display_name if u is not None else '' for u in users]


    def users_to_tags(self, users):
        """Convert a list of Users to a list of tags (str).
        """
        return ["<@!{}>".format(u.id) if u is not None else '' for u in users]


    def user_to_tag(self, user):
        """Convert a list of Users to a list of tags (str).
        """
        return "<@!{}>".format(user.id) if user is not None else ''


    async def on_ready(self):
        """Set up variables and logging
        """
        self.log_debug('Running {}'.format(self.on_ready.__name__))
        await self.wait_until_ready()

        self.log_debug('Logged in as {}'.format(self.user.name))

        channel = self.get_channel(int(self.CHANNEL))
        self.log_debug('Channel is {}'.format(channel))

        yesterday = date.today() - timedelta(days=1)
        doc_ref = self.db.document('odp-scheduler/messages/poll_messages/{}'.format(yesterday.strftime("%Y%m%d")))
        doc = doc_ref.get().to_dict()

        if doc == None:
            self.log_debug("Couldn't find a Discord message for date {}".format(yesterday.strftime("%Y%m%d")))
            msg_id = None
            await self.shudown_bot()
        else:
            msg_id = doc['id']
            self.log_debug('Read last message ID {} in channel'.format(msg_id))

        if msg_id == 'debug_mode':
            self.DEBUG = True

        self.log_debug('Calling {} on channel.'.format(self.manage_schedule.__name__))
        await self.manage_schedule(channel, msg_id)

        self.shudown_bot()


    async def shudown_bot(self):
        self.log_debug('Shutdown poll bot.')
        await self.close()

    
    def log_debug(self, msg):
        self.LOG.log_text(msg, severity="DEBUG")


    def log_error(self, msg):
        self.LOG.log_text(msg, severity="DEBUG")