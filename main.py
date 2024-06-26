from dabc import dabc_drawings, from_productList_to_Embeds, read_dabc_pdf, whiskey_allocated, whiskey_limited, from_pdfList_to_Embeds, is_third_wednesday
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
    "DRAWINGS_HOOK"
)

for var in envVars:
    if not getenv(var):
        raise Exception(f"Missing env variable: {var}")

def allocated():
  color = random_color()
  whiskeyList = whiskey_allocated()
  for whiskey in whiskeyList:
    embedList = from_productList_to_Embeds(whiskey, color)
    send_discord('Allocated', embedList)

def pdf(args=None):
  if is_third_wednesday(datetime.today()) or args.pdf:
    color = random_color()
    pdfList = read_dabc_pdf()
    for product in pdfList:
      embedList = from_pdfList_to_Embeds(product, color)
      send_discord('Allocated', embedList)

def limited():
  color = random_color()
  whiskeyList = whiskey_limited()
  for whiskey in whiskeyList:
    embedList = from_productList_to_Embeds(whiskey, color)
    send_discord('Limited', embedList)

def drawings():
  drawings = dabc_drawings()
  if drawings:
    send_discord('Drawings', drawings)
  else:
    logger.info("No Drawings today")

def parse_args(args):
  parser = argparse.ArgumentParser(description='Bot')
  parser.add_argument('--now', action='store_true', help='Run Now')
  parser.add_argument('--pdf', action='store_true', help='PDF')
  args = parser.parse_args()
  return args

def main(args):
  args = parse_args(args)
  logger.info("Starting Bot...")

  if args.now:
    allocated()
    limited()
    drawings()
  elif args.pdf:
    pdf(args)
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