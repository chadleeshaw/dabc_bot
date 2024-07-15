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
    "ALLOCATED_HOOK",
    "LIMITED_HOOK",
    "DRAWINGS_HOOK",
)

for var in envVars:
    if not getenv(var):
        raise Exception(f"Missing env variable: {var}")

def postAllocated():
  color = random_color()
  allocatedList = allocated()
  for a in allocatedList:
    embedList = from_productList_to_Embeds(a, color)
    send_discord('Allocated', embedList)

def postLimited():
  color = random_color()
  limitedList = limited()
  for l in limitedList:
    embedList = from_productList_to_Embeds(l, color)
    send_discord('Limited', embedList)

def postDrawings():
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
    postAllocated()
    postLimited()
    postDrawings()
  else:
    time = "11:00"

    if getenv('BOOZE_TIME'):
      time = getenv('BOOZE_TIME')

    schedule.every().day.at(time).do(postAllocated)
    schedule.every().day.at(time).do(postLimited)
    schedule.every().day.at(time).do(postDrawings)

    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == "__main__":
  main(argv[1:])