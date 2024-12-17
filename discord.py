from dataclasses import dataclass, asdict
from os import environ as env
from typing import List
import random
import json
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
    fields: List[Field]

    @classmethod
    def from_product(cls, product: dict, color: str = '15838749') -> 'Embed':
        sku = product.get('sku')
        return cls(
            color=color,
            url=f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/GetDetailUrl?sku={sku}',
            title=product.get('name'),
            fields=[
                Field(name='Price:', value=str(product.get('currentPrice')), inline=True),
                Field(name='StoreQty:', value=str(product.get('storeQty')), inline=True)
            ]
        )

    @classmethod
    def from_drawings(cls, color: str = '15838749') -> 'Embed':
        return cls(
            color=color,
            url='https://webapps2.abc.utah.gov/ProdApps/RareHighDemandProducts',
            title='Drawing(s) Detected on DABC Website',
            fields=[]
        )

@dataclass
class DiscordWebhook:
    username: str
    content: str
    embeds: List[Embed]

def generate_random_color() -> str:
    """Generate a random color in hexadecimal format."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return str((r * 256 * 256) + (g * 256) + b)

def send_discord_message(type: str, embed_list: List[Embed]) -> None:
    """Send a message to Discord using the specified webhook."""
    logger = my_logger(__name__)
    webhook_url = env.get(f"{type.upper()}_HOOK", "")

    discord_message = DiscordWebhook(
        username=type.title(),
        content='',
        embeds=embed_list
    )

    discord_json = json.dumps(asdict(discord_message))

    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(url=webhook_url, headers=headers, data=discord_json)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.info(response.text)
        logger.error(f"Failed to send Discord message: {err}")
    else:
        logger.info(f"Discord message sent successfully. Status code: {response.status_code}")

if __name__ == "__main__":
    pass