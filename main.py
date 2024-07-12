from unicodedata import category
from dabc import dabc_drawings, from_productList_to_Embeds, allocated, limited
from discord import send_discord, random_color
from datetime import datetime
from time import sleep
from os import getenv
from sys import argv
import schedule
import argparse


from logs import my_logger

logger = my_logger(__name__)

envVars = (
    "BOURBON_ALLOCATED_HOOK",
    "BOURBON_LIMITED_HOOK",
    "DRAWINGS_HOOK",
    "TEQUILA_ALLOCATED_HOOK",
    "TEQUILA_LIMITED_HOOK",
)

for var in envVars:
    if not getenv(var):
        raise Exception(f"Missing env variable: {var}")

def allocated():
  color = random_color()
  whiskeyList = allocated(category='LA')
  for whiskey in whiskeyList:
    embedList = from_productList_to_Embeds(whiskey, color)
    send_discord('Boubon_Allocated', embedList)
  tequilaList = allocated(category='AP')
  for tequila in tequilaList:
    embedList = from_productList_to_Embeds(tequila, color)
    send_discord('Tequila_Allocated', embedList)

def limited():
  color = random_color()
  whiskeyList = limited(category='LA')
  for whiskey in whiskeyList:
    embedList = from_productList_to_Embeds(whiskey, color)
    send_discord('Bourbon_Limited', embedList)
  tequilaList = limited(category='AP')
  for tequila in tequilaList:
    embedList = from_productList_to_Embeds(tequila, color)
    send_discord('Tequila_Limited', embedList)

def drawings():
  drawings = dabc_drawings()
  if drawings:
    send_discord('Drawings', drawings)
  else:
    logger.info("No Drawings today")

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
    drawings()
  else:
    time = "11:00"

    if getenv('BOOZE_TIME'):
      time = getenv('BOOZE_TIME')

    schedule.every().day.at(time).do(allocated)
    schedule.every().day.at(time).do(limited)
    schedule.every().day.at(time).do(drawings)

    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == "__main__":
  main(argv[1:])