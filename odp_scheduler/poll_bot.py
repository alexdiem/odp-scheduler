import discord
from discord.ext import commands

import os

from datetime import date


class PollBot(commands.Bot):

    def __init__(self, command_prefix, self_bot, options, db, log, debug=False):
        self.DEBUG = debug
        self.db = db
        self.LOG = log
        self.CHANNEL = os.getenv('SCHEDULER_CHANNEL')

        # Define poll
        self.POLL_TITLE = "Which days can you captain next week? The poll is open until midnight"
        with open(options, 'r') as f:
            self.POLL_OPTIONS = eval(f.read())
        self.POLL_MESSAGE = self.POLL_TITLE +\
            "\n\n" + "\n".join(f'{k}: {v}' for k,v in self.POLL_OPTIONS.items())

        # Instantiate bot
        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)


    async def send_poll(self, channel):
        """Send poll message to channel and add poll reactions 
        """
        self.log_debug('Running {}.'.format(self.send_poll.__name__))
        await self.wait_until_ready()

        self.log_debug('Send message to channel: \n{}'.format(self.POLL_MESSAGE))

        today = date.today()
        doc_ref = self.db.document('odp-scheduler/messages/poll_messages/{}'.format(today.strftime("%Y%m%d")))
        if not self.DEBUG:
            m = await channel.send(self.POLL_MESSAGE)
            doc_ref.set({'id': m.id})

            for emoji in self.POLL_OPTIONS.keys():
                self.LOG.log_text('Add reaction to poll: {}'.format(emoji))
                await m.add_reaction(emoji)
        else:
            doc_ref.set({'id': 'debug_mode'})


    async def on_ready(self):
        """Set up variables and logging
        """
        self.log_debug('Running {}'.format(self.on_ready.__name__))
        await self.wait_until_ready()

        self.log_debug('Logged in as {}'.format(self.user.name))

        channel = self.get_channel(int(self.CHANNEL))
        self.log_debug('Channel is {}'.format(channel))

        self.log_debug('Calling {} on channel.'.format(self.send_poll.__name__))
        await self.send_poll(channel)

        self.log_debug('Shutdown poll bot.')
        await self.close()


    def log_debug(self, msg):
        self.LOG.log_text(msg, severity="DEBUG")
