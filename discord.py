import json
import random
from dataclasses import asdict, dataclass
from os import environ as env
from typing import Any

import requests

from logs import my_logger


@dataclass
class Field:
    name: str
    value: str
    inline: bool


@dataclass
class Embed:
    color: str
    url: str
    title: str
    description: str
    fields: list[Field]

    @classmethod
    def from_product(cls, product: dict[str, Any], color: str = '15838749') -> 'Embed':
        sku = product.get('sku')
        base_url = env.get('DABC_PROXY_URL', 'https://dabc.chadshaw.net').rstrip('/')
        return cls(
            color=color,
            url=f'{base_url}/dabc/{sku}',
            title=str(product.get('name', '')),
            description='',
            fields=[
                Field(name='Price:', value=str(product.get('currentPrice')), inline=True),
                Field(name='StoreQty:', value=str(product.get('storeQty')), inline=True),
            ],
        )

    @classmethod
    def from_product_description(cls, description: str, color: str = '15838749') -> 'Embed':
        return cls(
            color=color,
            url='',
            title='',
            description=f'```\n{description}\n```',
            fields=[],
        )

    @classmethod
    def from_drawings(cls, color: str = '15838749') -> 'Embed':
        return cls(
            color=color,
            url='https://webapps2.abc.utah.gov/ProdApps/RareHighDemandProducts',
            title='Drawing(s) Detected on DABC Website',
            description='',
            fields=[],
        )


@dataclass
class DiscordWebhook:
    username: str
    content: str
    embeds: list[Embed]


def generate_random_color() -> str:
    """Generate a random color in hexadecimal format."""
    r = random.randint(0, 255)  # noqa: S311
    g = random.randint(0, 255)  # noqa: S311
    b = random.randint(0, 255)  # noqa: S311
    return str((r * 256 * 256) + (g * 256) + b)


def send_discord_message(type: str, embed_list: list[Embed]) -> None:
    """Send a message to Discord using the specified webhook."""
    logger = my_logger(__name__)
    webhook_url = env.get(f"{type.upper()}_HOOK", "")

    discord_message = DiscordWebhook(
        username=type.title(),
        content='',
        embeds=embed_list[:10],
    )

    discord_json = json.dumps(asdict(discord_message))

    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(url=webhook_url, headers=headers, data=discord_json, timeout=30)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.info(response.text)
        logger.error(f"Failed to send Discord message: {err}")
    else:
        logger.info(f"Discord message sent successfully. Status code: {response.status_code}")


if __name__ == "__main__":
    pass
