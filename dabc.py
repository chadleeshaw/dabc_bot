from typing import List, Dict, Any
from bs4 import BeautifulSoup
from discord import Embed
import requests
import re
import urllib.parse
from operator import itemgetter
from logs import my_logger

logger = my_logger(__name__)

# Constants
CATEGORIES = {
    'AW': 'Whiskey',  # Whiskey
    'AP': 'Tequila',  # Tequila
}

def dabc_request(method: str, url: str, data: str = None) -> requests.Response:
    """
    Send a request to DABC with specified method, URL, and data.

    :param method: HTTP method ('GET' or 'POST')
    :param url: API endpoint URL
    :param data: Data to send with POST requests
    :return: Response object from requests
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    response = requests.request(method, url, headers=headers, data=data)
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(f"Error in DABC request: {err}")
    
    return response

def is_unwanted_product(product: Dict[str, Any]) -> bool:
    """
    Check if the product should be skipped based on unwanted categories.

    :param product: Dictionary containing product details
    :return: True if the product is unwanted, False otherwise
    """
    unwanted = ['SCOTCH', 'WINE', 'BEER']
    return any(unwanted_item in product.get('name', '').upper() or 
            unwanted_item in product.get('displayGroup', '').upper() for unwanted_item in unwanted)

def handle_product_response(response: requests.Response) -> List[Dict[str, Any]]:
    """
    Process the DABC response and filter out unwanted products.

    :param response: The response object from DABC request
    :return: List of filtered product dictionaries
    """
    try:
        data = response.json()
        if data.get('recordsTotal') == 0:
            logger.warning('DABC request returned zero results')
        
        products = data.get('data', [])
        return [
            {k: v for k, v in product.items() if k not in ['onSpa', 'newItem', 'inStock']}
            for product in products if not is_unwanted_product(product)
        ]
    except ValueError:
        logger.error("DABC request did not return JSON")
        return []

def submit_dabc_query(category: str, status: str = '') -> requests.Response:
    """
    Submit a query to the DABC product table after URL encoding the parameters.
    
    :param category: The category to filter by
    :param status: The status to filter by (optional)
    :return: The response from the DABC API
    """
    base_url = "https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/LoadProductTable"
    
    params = {
        "draw": "8",
        "columns[0][data]": "name",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "sku",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "false",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "displayGroup",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "status",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "warehouseQty",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "true",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "storeQty",
        "columns[5][name]": "",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "true",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "columns[6][data]": "onOrderQty",
        "columns[6][name]": "",
        "columns[6][searchable]": "true",
        "columns[6][orderable]": "true",
        "columns[6][search][value]": "",
        "columns[6][search][regex]": "false",
        "columns[7][data]": "currentPrice",
        "columns[7][name]": "",
        "columns[7][searchable]": "true",
        "columns[7][orderable]": "true",
        "columns[7][search][value]": "",
        "columns[7][search][regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "start": "0",
        "length": "200",
        "search[value]": "",
        "search[regex]": "false",
        "item_code": "",
        "item_name": "",
        "category": f"{category}",
        "sub_category": "",
        "price_min": "",
        "price_max": "",
        "on_spa": "false",
        "new_items": "false",
        "in_stock": "false",
        "status": f"{status}", 
    }
    # Encode the parameters
    encoded_body = urllib.parse.urlencode(params)
    
    # Make the request with the encoded body
    return dabc_request('POST', base_url, encoded_body)

def is_product_in_store(product: Dict[str, Any]) -> bool:
    """Check if the product is available in-store."""
    return product.get('storeQty', 0) > 0

def check_for_drawings() -> bool:
    """
    Check if there are current or future drawings on the DABC website.

    :return: True if drawings are found, False otherwise
    """
    url = 'https://webapps2.abc.utah.gov/ProdApps/RareHighDemandProducts'
    response = dabc_request('GET', url)
    soup = BeautifulSoup(response.text, 'html.parser')
    future = soup.find('div', id='future')
    current = soup.find('div', id='current')

    return 'No Future' not in str(future) or 'No Current' not in str(current)

def get_allocated_products() -> List[List[Dict[str, Any]]]:
    """
    Retrieve and organize all allocated products, ensuring single-store SKUs aren't from club stores.

    :return: List of lists where each inner list contains up to 10 products
    """
    allocated_products = []
    final_allocated = []

    # Direct from 'LA' category
    allocated_items = submit_dabc_query('LA', '')
    for item in handle_product_response(allocated_items):
        if is_product_in_store(item):
            stores = scrape_store_locations(allocated_items, item.get('sku', ''))
            if len(stores) > 0:
                final_allocated.append(item)

    # From specified categories with 'A' status
    for cat in CATEGORIES.keys():
        products = handle_product_response(submit_dabc_query(cat, 'A'))
        for product in products:
            if is_product_in_store(product):
                stores = scrape_store_locations(allocated_items, product.get('sku', ''))
                if len(stores) > 0:
                    allocated_products.append(product)

    all_allocated = sorted(allocated_products + final_allocated, key=itemgetter('name'))
    return [all_allocated[i:i+10] for i in range(0, len(all_allocated), 10)]

def get_limited_products() -> List[List[Dict[str, Any]]]:
    """
    Retrieve and organize all limited products, ensuring single-store SKUs aren't from club stores.

    :return: List of lists where each inner list contains up to 10 products
    """
    limited_products = []
    final_limited = []

    # Direct from 'LT' category
    limited_offers = submit_dabc_query('LT', '')
    for item in handle_product_response(limited_offers):
        if is_product_in_store(item):
            stores = scrape_store_locations(limited_offers, item.get('sku', ''))
            if len(stores) >0:
                final_limited.append(item)

    # From specified categories with 'L' status
    for cat in CATEGORIES.keys():
        products = handle_product_response(submit_dabc_query(cat, 'L'))
        for product in products:
            if is_product_in_store(product):
                stores = scrape_store_locations(limited_offers, product.get('sku', ''))
                if len(stores) > 0:
                    limited_products.append(product)

    all_limited = sorted(limited_products + final_limited, key=itemgetter('name'))
    return [all_limited[i:i+10] for i in range(0, len(all_limited), 10)]

def generate_drawing_embeds() -> List[Embed]:
    """Generate embeds if there are drawings."""
    if check_for_drawings():
        return [Embed.from_drawings()]
    return []

def products_to_embeds(products: List[Dict[str, Any]], color: str) -> List[Embed]:
    """Convert a list of products to Discord Embeds."""
    return [Embed.from_product(product, color) for product in products]

def scrape_store_locations(response: requests.Response, sku: str) -> List[Dict[str, str]]:
    """
    Scrape store locations for a given SKU.

    :param response: Response object containing cookies for the request
    :param sku: Product SKU to search for
    :return: List of dictionaries containing store information
    """
    detail_url = f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/Products/GetDetailUrl?sku={sku}'
    sku_response = requests.get(detail_url, cookies=response.cookies, headers=response.headers)
    sku_response.raise_for_status()

    store_url = sku_response.text
    store_response = requests.get(store_url, cookies=sku_response.cookies, headers=sku_response.headers)
    store_response.raise_for_status()

    soup = BeautifulSoup(store_response.text, 'html.parser')
    table = soup.find('table', id='storeTable')
    rows = table.find_all('tr')[1:] if table else []
    
    headings = ('store', 'name', 'address', 'city', 'phone', 'store qty', 'pin')
    stores = []
    for row in rows:
        row_data = [re.sub(r"(\xa0)|(\n)|,", "", td.text) for td in row.find_all('td')]
        store_dict = dict(zip(headings, row_data))
        if not is_club_store(store_dict):
            stores.append({
                "name": store_dict['name'][:16],
                "city": store_dict['city'][:16],
                "store qty": store_dict['store qty'][:16],
                "address": store_dict['address'][:16],
            })
    return stores

def is_club_store(store: Dict[str, str]) -> bool:
    """Check if the store is a club store."""
    return '(Club' in store.get('name', '')

if __name__ == "__main__":
    pass