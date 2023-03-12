import os
import sys

import functions_framework
import firebase_admin
from firebase_admin import firestore

from dotenv import load_dotenv
from google.cloud import logging

from odp_scheduler.poll_bot import PollBot
from odp_scheduler.scheduler_bot import SchedulerBot


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG = eval(os.getenv('DEBUG'))


def run_bot(BotType, log_name):
    app = firebase_admin.initialize_app()
    db = firestore.client()
    
    logging_client = logging.Client()
    logging_client.setup_logging()
    logger = logging_client.logger(log_name)
    logger.log_text('Debug mode: {}'.format(DEBUG), severity="DEBUG")

    logger.log_text('Starting poll bot.', severity="DEBUG")
    bot = BotType(command_prefix='!', self_bot=False, options='POLL_OPTIONS_NOGRVL', db=db, log=logger, debug=DEBUG)
    bot.run(TOKEN)
    return "Success", 200


@functions_framework.http
def run_poll_bot(request):  
    log_name = "poll-bot-log"
    return run_bot(PollBot, log_name)


@functions_framework.http
def run_scheduler_bot(request):
    log_name = "scheduler-bot-log"
    return run_bot(SchedulerBot, log_name)