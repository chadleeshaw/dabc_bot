# Utah DABC Discord Bot

This Python script operates as a bot to post daily updates about Utah's Department of Alcoholic Beverage Control (DABC) limited, allocated items, and drawings to Discord channels. Designed for enthusiasts or anyone interested in tracking special liquor availability in Utah.

## Features
- **Daily Updates:** Automatically posts information about limited, allocated products, and drawings at a specified time each day.
- **Customizable Timing:** Can be set to run at a specific time via an environment variable.
- **Multiple Discord Webhooks:** Supports separate webhooks for allocated items, limited items, and drawings for better organization in Discord.

## Requirements
- **Python:** Ensure you have Python installed on your system or use a Docker container with Python pre-installed.
- **Discord Webhooks:** You need to create webhooks for each category (allocated, limited, drawings) in your Discord server where you want the updates to be posted.

## Environment Variables
The bot relies on these environment variables to function:

- `ALLOCATED_HOOK`: Discord webhook URL for allocated items.
- `LIMITED_HOOK`: Discord webhook URL for limited items.
- `DRAWINGS_HOOK`: Discord webhook URL for drawing notifications.
- `BOOZE_TIME` (optional): Time to run the bot daily, default is `11:00` (HH:MM format).
- `TZ` (optional but recommended): Set your timezone to ensure correct scheduling, e.g., `America/Denver`.

## Installation and Usage

### Using Docker

If you prefer containerization, you can use Docker to run this bot:

```bash
docker run -d \
  -e BOOZE_TIME=12:00 \
  -e TZ=America/{yourtimezone} \
  -e ALLOCATED_HOOK={yourdiscordwebhook} \
  -e LIMITED_HOOK={yourdiscordwebhook} \
  -e DRAWINGS_HOOK={yourdiscordwebhook} \
  ghcr.io/chadleeshaw/dabc_bot:latest
