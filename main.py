from unicodedata import category
from dabc import get_allocated_products, get_limited_products, products_to_embeds, generate_drawing_embeds
from discord import send_discord_message, generate_random_color
import schedule
import argparse
import os
from sys import argv
from time import sleep
from logs import my_logger

logger = my_logger(__name__)

# Environment variables required for the script
REQUIRED_ENV_VARS = (
    "ALLOCATED_HOOK",
    "LIMITED_HOOK",
    "DRAWINGS_HOOK",
)

# Check for required environment variables
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing environment variable: {var}")

def post_allocated_items():
    """
    Post allocated items to Discord with random color embeds.
    """
    color = generate_random_color()
    for batch in get_allocated_products():
        embeds = products_to_embeds(batch, color)
        send_discord_message('Allocated', embeds)

def post_limited_items():
    """
    Post limited items to Discord with random color embeds.
    """
    color = generate_random_color()
    for batch in get_limited_products():
        embeds = products_to_embeds(batch, color)
        send_discord_message('Limited', embeds)

def post_drawings():
    """
    Post about drawings if any are available.
    """
    drawings = generate_drawing_embeds()
    if drawings:
        send_discord_message('Drawings', drawings)
    else:
        logger.info("No Drawings today")

def parse_arguments(args):
    """
    Parse command line arguments.

    :param args: List of command line arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Bot for posting DABC updates to Discord')
    parser.add_argument('--now', action='store_true', help='Run the bot immediately')
    return parser.parse_args(args)

def main(args):
    """
    Main function to control the bot's execution.

    :param args: Command line arguments
    """
    parsed_args = parse_arguments(args)
    logger.info("Starting Bot...")

    if parsed_args.now:
        post_allocated_items()
        post_limited_items()
        post_drawings()
    else:
        # Get run time from environment variable or use default
        run_time = os.getenv('BOOZE_TIME', '11:00')

        schedule.every().day.at(run_time).do(post_allocated_items)
        schedule.every().day.at(run_time).do(post_limited_items)
        schedule.every().day.at(run_time).do(post_drawings)

        while True:
            schedule.run_pending()
            sleep(1)

if __name__ == "__main__":
    main(argv[1:])