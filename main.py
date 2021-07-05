# Run Showcase Bot

import os
import traceback
import logging
from datetime import datetime

from lib import utils
from discordbot.bot import ShowcaseBot

# Main Program
def run(logger):

    BOT_PREFIX, TOKEN = utils.get_discord_config()

    logger.info("Starting disocrd bot...")

    bot = ShowcaseBot(BOT_PREFIX, TOKEN)
    bot.run()

if __name__ == '__main__':

    try:
        # Setup Logging

        timeNow = str(datetime.now()).replace(" ", "_").replace(":", "-")

        config = utils.get_config()

        if(config["app"]["logging"]):
            logging.basicConfig(
                handlers=[logging.FileHandler(filename=f"logs/{timeNow}.txt", 
                                                 encoding='utf-8', mode='a+'), 
                            logging.StreamHandler()],
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s:%(name)s - %(message)s'
                )
        else:
            logging.basicConfig(
                handlers=[logging.StreamHandler()],
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s:%(name)s - %(message)s'
                )
        logging.info(f"Showcase bot logs - {timeNow}")

        run(logging.getLogger(__name__))        

    except Exception as e:
        logging.error(str(e) + "\n\n" + traceback.format_exc())