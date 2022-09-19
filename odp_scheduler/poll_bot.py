import discord
from discord.ext import commands

import os


class PollBot(commands.Bot):

    def __init__(self, command_prefix, self_bot, options, log, debug=False):
        self.DEBUG = debug
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
        self.LOG.log_text('Running {}.'.format(self.send_poll.__name__), severity="DEBUG")
        await self.wait_until_ready()

        self.LOG.log_text('Send message to channel: \n{}'.format(self.POLL_MESSAGE), severity="DEBUG")
        m = await channel.send(self.POLL_MESSAGE)

        for emoji in self.POLL_OPTIONS.keys():
            self.LOG.log_text('Add reaction to poll: {}'.format(emoji), severity="DEBUG")
            await m.add_reaction(emoji)


    async def on_ready(self):
        """Set up variables and logging
        """
        self.LOG.log_text('Running {}'.format(self.on_ready.__name__), severity="DEBUG")
        await self.wait_until_ready()

        self.LOG.log_text('Logged in as {}'.format(self.user.name), severity="DEBUG")

        channel = self.get_channel(int(self.CHANNEL))
        self.LOG.log_text('Channel is {}'.format(channel), severity="DEBUG")

        if not self.DEBUG:
            self.LOG.log_text('Calling {} on channel.'.format(self.send_poll.__name__), severity="DEBUG")
            await self.send_poll(channel)

        self.LOG.log_text('Shutdown poll bot.', severity="DEBUG")
        await self.close()