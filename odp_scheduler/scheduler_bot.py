import discord
from discord.ext import commands

import json
import os
import random

from datetime import date


class SchedulerBot(commands.Bot):

    def __init__(self, command_prefix, self_bot, options, log, debug=False):
        self.DEBUG = debug
        self.LOG = log
        self.CHANNEL = os.getenv('SCHEDULER_CHANNEL')
        self.SCHEDULER_MSG = "@channel I'm a level 1 naive scheduling bot, and I make mistakes. " +\
                "<@!766548029116907570> will help me fix it.\n"

        with open(options, 'r') as f:
            self.POLL_OPTIONS = eval(f.read())
        
        self.RIDES = list(self.POLL_OPTIONS.values())
        self.SCHEDULE = dict((ride, []) for ride in self.RIDES)
        self.CAPTAINS_PER_RIDE = zip(self.RIDES, [1, 1, 2, 1, 1])

        # Instantiate bot
        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)


    async def manage_schedule(self, channel, msg_id):
        """Read reactions on last poll message 
        """
        self.LOG.log_text('Running {}.'.format(self.manage_schedule.__name__), severity='DEBUG')
        await self.wait_until_ready()

        try:
            msg = await channel.fetch_message(msg_id)
        except discord.errors.NotFound:
            self.LOG.log_text("Discord error: Message ID {} not found.".format(msg_id), severity='ERROR')
            await self.close()
            exit()
            
        self.LOG.log_text("Got message with ID {}".format(msg_id), severity='DEBUG')
            
        reactions = msg.reactions

        self.LOG.log_text('Calling {} on channel.'.format(self.read_reactions.__name__), severity='DEBUG')
        avail = await self.read_reactions(reactions)

        for ride, n_cap in self.CAPTAINS_PER_RIDE:
            self.LOG.log_text('Calling {} on channel for {}.'.
                format(self.create_ride_schedule.__name__, ride), severity='DEBUG')
            captains = await self.create_ride_schedule(ride, n_cap, avail)
            self.SCHEDULE[ride] = captains


        self.LOG.log_text('Calling {}.'.format(self.update_logs.__name__), severity='DEBUG')
        self.update_logs()
        
        if not self.DEBUG:
            self.LOG.log_text('Calling {} on channel.'.format(self.post_schedule.__name__), severity='DEBUG')
            await self.post_schedule(channel)


    async def read_reactions(self, reactions):
        """Read reactions from scheduler poll
        """
        self.LOG.log_text('Running {}.'.format(self.read_reactions.__name__), severity='DEBUG')
        await self.wait_until_ready()

        self.LOG.log_text('Getting availability from poll.', severity='DEBUG')
        emojis = list(self.POLL_OPTIONS.keys())
        avail = dict((ride, []) for ride in self.RIDES)
        for reaction in reactions:
            ride_index = ''
            try:
                ride_index = emojis.index(reaction.emoji)
            except ValueError:
                self.LOG.log_text("Invalid reaction found: {}".format(reaction.emoji), severity='ERROR')
                continue

            users = [user async for user in reaction.users()]
            for user in users:
                if not user.bot:
                    avail[self.RIDES[ride_index]].append(user)
        
        self.LOG.log_text('Availability is: {}'.format(
            "\n".join(f'{k}: {self.users_to_names(v)}' for k,v in avail.items())
        ), severity='DEBUG')
        return avail


    async def create_ride_schedule(self, ride, n_cap, avail):
        """Create road captain schedule
        """
        self.LOG.log_text('Running {}.'.format(self.create_ride_schedule.__name__), severity='DEBUG')
        await self.wait_until_ready()

        self.LOG.log_text('Choosing road captains for {}'.format(ride), severity='DEBUG')
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
                    self.LOG.log_text('Scheduled {} on {}. Removing them from {}'.
                        format(captain.display_name, ride, s), severity='DEBUG')
                    avail[s].remove(captain)

        self.LOG.log_text(
            "Road captains for {} are {}".format(ride, self.users_to_names(captains),
            severity='DEBUG')
        )
        return captains


    def prioritise_absence(self, ride, avail):
        """Prioritise captains that have been absent longer than others. Not yet in use.
        """
        self.LOG.log_text('Running {}.'.format(self.prioritise_absence.__name__), severity='DEBUG')


        with open('schedule') as f:
            schedule = [json.loads(line) for line in f]
        
        print(schedule)


    def update_logs(self):
        """Update log files.
        """
        self.LOG.log_text('Running {}.'.format(self.update_logs.__name__), severity='DEBUG')

        # log schedule to file
        self.LOG.log_text('Saving schedule to log.', severity='DEBUG')

        printable_schedule = self.SCHEDULE.copy()
        for ride in printable_schedule:
            printable_schedule[ride] = self.users_to_names(printable_schedule[ride])
        printable_schedule['date'] = str(date.today())

        json_schedule = json.dumps(printable_schedule)
        with open("schedule", 'a') as f:
            f.write('\n' + json_schedule)
        self.LOG.log_text(json_schedule, severity='DEBUG')


    async def post_schedule(self, channel):
        """Post schedule to channel.
        """
        self.LOG.log_text('Running {}.'.format(self.create_ride_schedule.__name__), severity='DEBUG')
        await self.LOG.wait_until_ready()

        msg = self.SCHEDULER_MSG + "\nRoad captains for this week are"

        schedule_post = self.SCHEDULE.copy()
        for ride in schedule_post:
            schedule_post[ride] = self.users_to_tags(schedule_post[ride])

        for k, v in schedule_post.items():
            msg += f"\n\n**{k}**\n" +\
                    "\n".join(f'{c}' for c in v)

        self.LOG.log_text('Send message to channel: \n{}'.format(msg), severity='DEBUG')
        #m = await channel.send(msg)


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
        self.LOG.log_text('Running {}'.format(self.on_ready.__name__), severity='DEBUG')
        await self.wait_until_ready()

        self.LOG.log_text('Logged in as {}'.format(self.user.name), severity='DEBUG')

        channel = self.get_channel(int(self.CHANNEL))
        self.LOG.log_text('Channel is {}'.format(channel), severity='DEBUG')

        msg_id = channel.last_message_id
        self.LOG.log_text('Read last message ID {} in channel'.format(msg_id), severity='DEBUG')

        self.LOG.log_text('Calling {} on channel.'.format(self.manage_schedule.__name__), severity='DEBUG')
        await self.manage_schedule(channel, msg_id)

        self.LOG.log_text('Shutdown poll bot.', severity='DEBUG')
        await self.close()