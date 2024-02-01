from table2ascii import table2ascii, PresetStyle, Alignment
from dataclasses import dataclass, asdict
from os import environ as env
from logs import my_logger
from tkinter import N
import requests


@dataclass
class Thumbnail:
  url: str

@dataclass
class Footer:
  text: str
  icon_url: str

@dataclass
class Embeds:
  color: str
  title: str
  url: str
  description: str
  thumbnail: Thumbnail
  footer: Footer

  @classmethod
  def from_allocated(cls: classmethod, product: dict) -> object:
    storeList = []
    for store in product.get('stores'):
      storeList.append(list(store.values()))
    asciitable = table2ascii(
      header=['City', 'StoreQty', 'Address'],
      body=storeList,
      first_col_heading=False,
      style=PresetStyle.thin_compact,
      alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.LEFT],
    )
    description = f"""Price: `${product.get('currentPrice')}`
      DisplayGroup: `{product.get('displayGroup')}`
      Status: `{product.get('status')}`
      Stores:
      ```{asciitable}```
    """
    footer = f"StoreQty: {product.get('storeQty')}     WarehouseQty: {product.get('warehouseQty')}     OnOrder: {product.get('onOrderQty')}"
    return cls(
      color = '12745742',
      url = '',
      thumbnail = Thumbnail(
        url = '',
      ),
      title = product.get('name'),
      description = description,
      footer = Footer(
        text = footer,
        icon_url = '',
      ) 
    )

@dataclass
class Discord:
  username: str
  content: str 
  embeds: list[Embeds]

def send_discord(type: str, embedList: list[Embeds] = None, contentStr: str = None) -> None:
  logger = my_logger(__name__)
  webHook = env.get(f"{type.upper()}_HOOK", "")

  if contentStr and embedList:
    logger.error("Both embed and content passed for Discord message")

  if contentStr:
    contentStr = '```' + contentStr + '```'

  discord = Discord(
    username = f"{type.title()} Whiskey",
    content = contentStr,
    embeds = embedList
  )

  logger.debug(discord)
  discord_req = requests.post(webHook, json=asdict(discord))

  try:
    discord_req.raise_for_status()
  except requests.exceptions.HTTPError as err:
    logger.error(err)
  else:
    logger.info("Discord message sent successfully, code {}.".format(discord_req.status_code))