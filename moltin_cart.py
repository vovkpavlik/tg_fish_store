import os

import requests
from dotenv import load_dotenv
from pprint import pprint

from moltin_products import get_products
from moltin_products import get_moltin_token


def add_to_cart(access_token):    
    base_url = "https://api.moltin.com/v2/carts/:reference/items"
    
    sku = get_products(access_token)["data"][0]["sku"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "data": {
            "quantity": 1,
            "type": "cart_item",
            "sku": sku,
        }
    }

    add_to_cart = requests.post(base_url, headers=headers, json=data)
    add_to_cart.raise_for_status()


def get_cart(access_token):
    base_url = "https://api.moltin.com/v2/carts/:reference"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(base_url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_cart_items(access_token):
    base_url = "https://api.moltin.com/v2/carts/:reference/items"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    data = {
        "data": {
            "include": "tax_items"
        }
    }

    response = requests.get(base_url, headers=headers, data=data)
    response.raise_for_status()

    return response.json()


def main():
    load_dotenv()

    moltin_id = os.getenv("MOLTIN_ID")
    moltin_secret = os.getenv("MOLTIN_SECRET")
    moltin_token = get_moltin_token(moltin_secret, moltin_id)
    
    # add_to_cart(moltin_token)
    # pprint(get_cart(moltin_token))
    pprint(get_cart_items(moltin_token))



if __name__ == "__main__":
    main()