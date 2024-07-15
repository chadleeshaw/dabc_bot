from typing import Any
from bs4 import BeautifulSoup
from discord import Embeds
from logs import my_logger
from operator import itemgetter
import requests


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
    unwanted = ['SCOTCH', 'WINE', 'BEER', 'STATE STORE']
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
    # DABC website has an Allocated Items category
    allocatedItems= submit_dabc_query(category='LA', status='')
    aList = handle_product_request(allocatedItems)
    aFinal = list(filter(in_store, aList))

    # Append Allocated Items from CATEGORIES
    for category in CATEGORIES:
        allocatedReq= submit_dabc_query(category=category, status='A')
        allocatedList = handle_product_request(allocatedReq)
        allocatedFinal = allocatedFinal + list(filter(in_store, allocatedList))

    completeList = allocatedFinal + aFinal
    completeList.sort(key=itemgetter('name'))

    return [completeList[i:i+10] for i in range(0, len(completeList), 10)]

def limited() -> list[list[dict]]:
    limitedFinal = []
    # DABC website has a category for Limited Offers
    limitedOffers = submit_dabc_query(category='LT', status='')
    loList = handle_product_request(limitedOffers)
    loFinal = list(filter(in_store, loList))

    # Append Limited Items from CATEGORIES
    for category in CATEGORIES:
        limitedReq = submit_dabc_query(category=category, status='L')
        limitedList = handle_product_request(limitedReq)
        limitedFinal = limitedFinal + list(filter(in_store, limitedList))

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

# def from_pdfList_to_Embeds(pdfList: list[dict], color: str) -> list[Embeds]:
#     embedList = []
#     for product in pdfList:
#         embedList.append(Embeds.from_pdfList(product, color))
#     return embedList

# def is_third_wednesday(date: datetime) -> bool:
#     # Check if the date is a Wednesday.
#     if date.weekday() != 2:
#         return False

#     # Check if the date is between the 15th and 21st of the month.
#     if date.day < 15 or date.day > 21:
#         return False

#     # Check if the date is the third Wednesday of the month.
#     first_wednesday = date - datetime.timedelta(days=date.weekday())
#     third_wednesday = first_wednesday + datetime.timedelta(days=14)
#     return date == third_wednesday

# def is_nan(item: any):
#     if isinstance(item, float) and math.isnan(item):
#         return True
#     return False
    

# def read_dabc_pdf() -> list[dict]:
#     url = "https://abs.utah.gov/wp-content/uploads/Allocated-Items-List.pdf"
#     dfs = tabula.read_pdf(url, pages='all', stream=True, output_format='dataframe', user_agent='Custom User Agent')
#     header = dfs[0].values.tolist()[0]
#     for page in range(len(dfs)):
#         dfs[page].replace(r'\n', ' ', regex=True)
#         dfs[page] = dfs[page].iloc[1:]
#         dfs[page].columns = header
#     dfs_dict = dfs[0].drop_duplicates(subset='Item Name').to_dict(orient='records')
#     for item in dfs_dict:
#         if is_nan(item.get('Item Name')):
#             dfs_dict.remove(item)
#         if isinstance(item.get('Item Name'), str):
#             if len(item.get('Item Name').split()) < 2:
#                 dfs_dict.remove(item)
#         item.pop('County', None)
#         item.pop('(bottles)', None)
#         item.pop('Store', None)
#     print(dfs_dict)
#     return dfs_dict

if __name__ == "__main__":
    pass