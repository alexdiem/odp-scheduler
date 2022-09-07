import functions_framework
import os
import sys

from dotenv import load_dotenv
from google.cloud import logging

from odp_scheduler.poll_bot import PollBot


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging_client = logging.Client()
log_name = "poll-bot-log"
logger = logging_client.logger(log_name)


@functions_framework.http
def run_poll_bot(request):  
    DEBUG = False
    if '--debug' in sys.argv:
        DEBUG = True
    logger.log_text('Debug mode: {}'.format(DEBUG), severity="DEBUG")

    logger.log_text('Starting poll bot.', severity="DEBUG")
    bot = PollBot(command_prefix='!', self_bot=False, options='POLL_OPTIONS_SUMMER', log=logger, debug=DEBUG)
    bot.run(TOKEN)
    return "Success", 200