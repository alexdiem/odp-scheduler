import functions_framework
import logger
import os
import sys

from dotenv import load_dotenv

from odp_scheduler.poll_bot import PollBot


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

log = logger.setup_applevel_logger(file_name = 'app_debug.log')


@functions_framework.http
def run_poll_bot(request):  
    DEBUG = False
    if '--debug' in sys.argv:
        DEBUG = True
    log.debug('Debug mode: %s', DEBUG)

    log.debug('Starting poll bot.')
    bot = PollBot(command_prefix='!', self_bot=False, options='POLL_OPTIONS_SUMMER', log=log, debug=DEBUG)
    bot.run(TOKEN)
    return "Success", 200