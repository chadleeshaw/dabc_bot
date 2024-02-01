from table2ascii import table2ascii, PresetStyle, Alignment
from bs4 import BeautifulSoup
from functools import reduce
from discord import Discord, Embeds
from logs import my_logger
import requests
import re

logger = my_logger(__name__)

def dabc_request(method: str, url: str, data: str) -> requests:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    dabcReq = requests.request(method, url, headers=headers, data=data)

    try:
        dabcReq.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(err)

    return dabcReq

def handle_product_request(dabcReq: requests) -> list[dict]:
    try:
        if dabcReq.json():
            if dabcReq.json()['recordsTotal'] == 0:
                logger.warn('DABC request returned zero results')
            productList = dabcReq.json()['data']
            newList = []
            for product in productList:
                del product['onSpa']
                del product['newItem']
                del product['inStock']
                if 'SCOTCH' in product['displayGroup']:
                    continue
                newList.append(product)
            return newList
    except:
        logger.error("DABC request did not return JSON")

def handle_store_dict(store: dict) -> dict:
    ''' 
    Build shorter dictionary for Discord, max 16 chars
    '''
    return dict({
            "city": store.get('city')[:16],
            "store qty": store.get('store qty')[:16],
            "address": store.get('address')[:16],
        })

def get_allocated_whiskey() -> requests:
    url = "https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/LoadProductTable"
    body = "draw=8&columns%5B0%5D%5Bdata%5D=name&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=sku&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=displayGroup&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=status&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=warehouseQty&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=storeQty&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=onOrderQty&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=currentPrice&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=50&search%5Bvalue%5D=&search%5Bregex%5D=false&item_code=&item_name=&category=AW&sub_category=&price_min=&price_max=&on_spa=false&new_items=false&in_stock=false&status=A"
    return dabc_request('POST', url, body)

def get_limited_whiskey() -> requests:
    url = "https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/LoadProductTable"
    body = "draw=8&columns%5B0%5D%5Bdata%5D=name&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=sku&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=displayGroup&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=status&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=warehouseQty&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=storeQty&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=onOrderQty&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=currentPrice&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=50&search%5Bvalue%5D=&search%5Bregex%5D=false&item_code=&item_name=&category=AW&sub_category=&price_min=&price_max=&on_spa=false&new_items=false&in_stock=false&status=L"
    return dabc_request('POST', url, body)

def in_store(product: dict) -> bool:
    if product.get('storeQty') > 0:
            return True
    return False

def scrape_store_location(dabcReq: requests, sku: str) -> list[dict]:
    url= f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/GetDetailUrl?sku={sku}'
    skuReq = requests.get(url, cookies=dabcReq.cookies, headers=dabcReq.headers)
    skuReq.raise_for_status()

    storeReq = requests.get(skuReq.text, cookies=skuReq.cookies, headers=skuReq.headers)
    storeReq.raise_for_status()

    soup = BeautifulSoup(storeReq.text, 'html.parser')
    gdp = soup.find_all('table', id = 'storeTable')
    table1 = gdp[0]
    body = table1.find_all("tr")
    body_rows = body[1:]

    headings = ('store','name','address','city','phone','store qty','pin')

    storeList = []
    for row_num in range(len(body_rows)):
        row = []
        for row_item in body_rows[row_num].find_all("td"):
            aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
            row.append(aa)
        createDict = dict(zip(headings, row))
        storeDict = handle_store_dict(createDict)
        storeList.append(storeDict)

    return storeList

def whiskey_allocated():
    dabcReq = get_allocated_whiskey()
    rawList = handle_product_request(dabcReq)
    whiskeyList = list(filter(in_store, rawList))

    completeList = []
    for whiskey in whiskeyList:
        stores = scrape_store_location(dabcReq, whiskey.get('sku'))
        whiskey['stores'] = stores
        completeList.append((whiskey))
    
    logger.debug(completeList)
    return completeList

def whiskey_limited():
    dabcReq = get_limited_whiskey()
    rawList = handle_product_request(dabcReq)
    whiskeyList = list(filter(in_store, rawList))

    logger.debug(whiskeyList)
    return whiskeyList

def from_allocated_to_discord(productList: list[dict]) -> list[Embeds]:
    embededList = []
    for product in productList:
        embed = Embeds.from_allocated(product)
        embededList.append(embed)
    return embededList

def from_limited_to_discord(productList: list[dict]) -> str:
    newList = []
    for product in productList:
        del product['sku']
        del product['status']
        del product['displayGroup']
        del product['onOrderQty']
        del product['warehouseQty']
        newList.append(list(product.values()))

    logger.debug(newList)
    asciitable = table2ascii(
        header=['Name', 'StoreQty', 'CurrentPrice'],
        body=newList,
        first_col_heading=False,
        style=PresetStyle.thin_compact,
    )

    return asciitable