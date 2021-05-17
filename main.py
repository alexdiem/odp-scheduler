import logger
import poll_bot


def run_poll_bot():
    print("test")
    log = logger.setup_applevel_logger(file_name = 'app_debug.log')
    poll_bot.run_bot()