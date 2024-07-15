from typing import Any
from bs4 import BeautifulSoup
from discord import Embeds
from logs import my_logger
from operator import itemgetter
import requests
import re


CATEGORIES = (
    'AW', # Whiskey
    'AP', # Tequila
)

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

def unwanted_product(p):
    unwanted = ['SCOTCH', 'WINE', 'BEER']
    for u in unwanted:
        if u in p['name'] or u in p['displayGroup']:
            return True
    return False

def handle_product_request(dabcReq: requests) -> list[dict]:
    try:
        if dabcReq.json():
            newList = []
            if dabcReq.json().get('recordsTotal') == 0:
                logger.warn('DABC request returned zero results')
            productList = dabcReq.json().get('data', [])
            for product in productList:
                del product['onSpa']
                del product['newItem']
                del product['inStock']
                if unwanted_product(product):
                    continue
                newList.append(product)
            return newList
    except:
        logger.error("DABC request did not return JSON")

def submit_dabc_query(category: str, status: str) -> requests:
    url = "https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/LoadProductTable"
    body = f"draw=8&columns%5B0%5D%5Bdata%5D=name&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=sku&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=displayGroup&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=status&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=warehouseQty&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=storeQty&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=onOrderQty&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=currentPrice&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=200&search%5Bvalue%5D=&search%5Bregex%5D=false&item_code=&item_name=&category={category}&sub_category=&price_min=&price_max=&on_spa=false&new_items=false&in_stock=false&status={status}"
    return dabc_request('POST', url, body)

def in_store(product: dict) -> bool:
    if product.get('storeQty') > 0:
            return True
    return False

def is_drawings() -> bool:
    futureDrawing = True
    currentDrawing = True
    url= f'https://webapps2.abc.utah.gov/ProdApps/RareHighDemandProducts'
    dabcReq = dabc_request('GET', url, None)

    soup = BeautifulSoup(dabcReq.text, 'html.parser')
    future = soup.find_all('div', id = 'future')
    current = soup.find_all('div', id = 'current')

    if 'No Future' in str(future[0]):
        futureDrawing = False
    if 'No Current' in str(current[0]):
        currentDrawing = False

    return True if futureDrawing or currentDrawing else False

def allocated() -> list[list[dict]]:
    allocatedFinal = []
    aFinal = []
    # DABC website has an Allocated Items category
    allocatedItems= submit_dabc_query(category='LA', status='')
    aList = handle_product_request(allocatedItems)
    for item in aList:
        if in_store(item):
            storeList = scrape_store_location(allocatedItems, item.get('sku'))
            if storeList: 
                aFinal.append(item)


    # Append Allocated Items from CATEGORIES
    for category in CATEGORIES:
        allocatedReq = submit_dabc_query(category=category, status='A')
        allocatedList = handle_product_request(allocatedReq)
        for item in allocatedList:
            if in_store(item):
                storeList = scrape_store_location(allocatedReq, item.get('sku'))
                if storeList:
                    allocatedFinal.append(item)

    completeList = allocatedFinal + aFinal
    completeList.sort(key=itemgetter('name'))

    return [completeList[i:i+10] for i in range(0, len(completeList), 10)]

def limited() -> list[list[dict]]:
    limitedFinal = []
    loFinal = []
    # DABC website has a category for Limited Offers
    limitedOffers = submit_dabc_query(category='LT', status='')
    loList = handle_product_request(limitedOffers)
    for item in loList:
        if in_store(item):
            storeList = scrape_store_location(limitedOffers, item.get('sku'))
            if storeList: 
                loFinal.append(item)

    # Append Limited Items from CATEGORIES
    for category in CATEGORIES:
        limitedReq = submit_dabc_query(category=category, status='L')
        limitedList = handle_product_request(limitedReq)
        for item in limitedList:
            if in_store(item):
                storeList = scrape_store_location(limitedReq, item.get('sku'))
                if storeList:
                    limitedFinal.append(item)

    limitedComplete = limitedFinal + loFinal
    limitedComplete.sort(key=itemgetter('name'))

    return [limitedComplete[i:i+10] for i in range(0, len(limitedComplete), 10)]

def dabc_drawings() -> list[Embeds]:
    if is_drawings():
        return [Embeds.from_drawings()]
    return []

def from_productList_to_Embeds(productList: list[dict], color: str) -> list[Embeds]:
    embedList = []
    for product in productList:
        embedList.append(Embeds.from_product(product, color))
    return embedList

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

        if not isClubStore(storeDict):
            storeList.append(storeDict)

    return storeList

def handle_store_dict(store: dict) -> dict:
    return dict({
            "name": store.get('name'),
            "city": store.get('city')[:16],
            "store qty": store.get('store qty')[:16],
            "address": store.get('address')[:16],
        })

def isClubStore(store: dict) -> bool:
    if '(Club' in store.get('name'):
        return True
    return False

if __name__ == "__main__":
    pass