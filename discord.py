from dataclasses import dataclass, asdict
from os import environ as env
from logs import my_logger
import requests
import json


@dataclass
class Fields:
  name: str
  value: str
  inline: bool

@dataclass
class Embeds:
  color: str
  title: str
  url: str
  fields: list[Fields]

  @classmethod
  def from_product(cls: classmethod, product: dict, color='15838749') -> object:
    sku = product.get('sku')
    return cls(
      color = color,
      url = f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/GetDetailUrl?sku={sku}',
      title = product.get('name'),
      fields = [Fields(
          name = 'Name:',
          value = product.get('name'),
          inline = True,
        ),
        Fields(
          name = 'StoreQty',
          value = str(product.get('storeQty')),
          inline = True,
        ),
        Fields(
          name = 'Price',
          value = str(product.get('currentPrice')),
          inline = True,
        ),
      ]
    )

@dataclass
class Discord:
  username: str
  content: str 
  embeds: list[Embeds]

def send_discord(type: str, embedList: list[Embeds]) -> None:
  logger = my_logger(__name__)
  webHook = env.get(f"{type.upper()}_HOOK", "")

  discord = Discord(
    username = f"{type.title()} Whiskey",
    content = '',
    embeds = embedList
  )
  
  discordJson = json.dumps(asdict(discord))

  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  discord_req = requests.post(webHook, headers=headers, data=discordJson)

  try:
    discord_req.raise_for_status()
  except requests.exceptions.HTTPError as err:
    logger.info(discord_req.text)
    logger.error(err)
  else:
    logger.info("Discord message sent successfully, code {}.".format(discord_req.status_code))