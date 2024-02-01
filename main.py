from dabc import from_allocated_to_discord, from_limited_to_discord, whiskey_allocated, whiskey_limited
from discord import send_discord
from time import sleep
from os import getenv
from sys import argv
import schedule
import argparse


from logs import my_logger

logger = my_logger(__name__)

envVars = (
    "ALLOCATED_HOOK",
    "LIMITED_HOOK",
)

for var in envVars:
    if not getenv(var):
        raise Exception(f"Missing env variable: {var}")

def allocated():
  whiskeyList = whiskey_allocated()
  embedList = from_allocated_to_discord(whiskeyList)
  send_discord('Allocated', embedList=embedList)

def limited():
  whiskeyList = whiskey_limited()
  contentStr = from_limited_to_discord(whiskeyList)
  send_discord('Limited', contentStr=contentStr)

def parse_args(args):
  parser = argparse.ArgumentParser(description='Bot')
  parser.add_argument('--now', action='store_true', help='Run Now')
  args = parser.parse_args()
  return args

def main(args):
  args = parse_args(args)
  logger.info("Starting Bot...")

  if args.now:
    allocated()
    limited()
  else:
    time = "11:00"

    if getenv('BOOZE_TIME'):
      time = getenv('BOOZE_TIME')

    schedule.every().day.at(time).do(allocated)
    schedule.every().day.at(time).do(limited)

    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == "__main__":
  main(argv[1:])