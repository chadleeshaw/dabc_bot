import argparse
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from sys import argv
from time import sleep
from urllib.parse import parse_qs, urlparse

import requests
import schedule  # type: ignore[import-untyped]

from dabc import (
    generate_ascii_tables,
    generate_drawing_embeds,
    get_allocated_products,
    get_limited_products,
    products_to_embeds,
    products_to_embeds_tables,
)
from discord import generate_random_color, send_discord_message
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
        raise OSError(f"Missing environment variable: {var}")


def fetch_dabc_product_html(sku: str) -> str:
    """Fetch the rendered DABC product detail page using a session cookie."""
    session = requests.Session()
    detail_req = session.get(
        f"https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/GetDetailUrl?sku={sku}",
        timeout=30,
    )
    detail_req.raise_for_status()
    target_url = detail_req.text.strip()
    page_req = session.get(target_url, timeout=30)
    page_req.raise_for_status()
    html = page_req.text
    return html.replace(
        "<head>",
        '<head>\n    <base href="https://webapps2.abc.utah.gov/" />',
        1,
    )


class DabcProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler serving DABC product detail pages in one click."""

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        sku = ""
        match = re.match(r"^/(?:dabc/)?([0-9A-Za-z]+)$", parsed.path)
        if match:
            sku = match.group(1)
        elif parsed.path in ("/", "/dabc"):
            qs = parse_qs(parsed.query)
            sku = qs.get("sku", [""])[0]

        if not sku or not re.match(r"^[0-9A-Za-z]{3,12}$", sku):
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Usage: /dabc/<sku>")
            return

        try:
            body = fetch_dabc_product_html(sku).encode("utf-8")
        except Exception as err:
            logger.error(f"Failed to proxy DABC SKU {sku}: {err}")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Failed to load DABC product page")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        logger.debug(format % args)


def start_proxy_server() -> None:
    """Start background HTTP proxy server for DABC product links."""
    port = int(os.getenv("PORT", "5050"))
    server = ThreadingHTTPServer(("0.0.0.0", port), DabcProxyHandler)  # noqa: S104
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"DABC proxy server listening on port {port}")


def post_allocated_items() -> None:
    """Post allocated items to Discord with random color embeds."""
    color = generate_random_color()
    for batch in get_allocated_products():
        embeds = products_to_embeds(batch, color)
        send_discord_message('Allocated', embeds)


def post_limited_items() -> None:
    """Post limited items to Discord with random color embeds."""
    color = generate_random_color()
    tables = generate_ascii_tables(get_limited_products())
    for table in tables:
        embeds = products_to_embeds_tables(table, color)
        send_discord_message('Limited', embeds)


def post_drawings() -> None:
    """Post about drawings if any are available."""
    drawings = generate_drawing_embeds()
    if drawings:
        send_discord_message('Drawings', drawings)
    else:
        logger.info("No Drawings today")


def parse_arguments(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Bot for posting DABC updates to Discord')
    parser.add_argument('--now', action='store_true', help='Run the bot immediately')
    return parser.parse_args(args)


def main(args: list[str]) -> None:
    """Main function to control the bot's execution."""
    parsed_args = parse_arguments(args)
    logger.info("Starting Bot...")

    if parsed_args.now:
        post_allocated_items()
        post_limited_items()
        post_drawings()
    else:
        start_proxy_server()
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
