import os

import requests
from dotenv import load_dotenv
from pprint import pprint



def create_product(access_token):
    base_url = "https://api.moltin.com/pcm/products"
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "type": "product",
            "name": "Red fish",
            "slug": "red-fish",
            "sku": "fr1",
            "manage_stock": True,
            "description": "litle fish for your kitty",
            "price": [
                {
                    "amount": 10,
                    "currency": "USD"
                }
            ],
            "commodity_type": "physical"   
        }
    }


    add_new_product = requests.post(base_url, headers=headers, data=data)
    add_new_product.raise_for_status


def get_products(access_token):
    base_url = "https://api.moltin.com/pcm/products"
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    list_products = requests.get(base_url, headers=headers)
    list_products.raise_for_status

    return list_products.json()


def get_moltin_token(secret, id):
    base_url = "https://api.moltin.com/oauth/access_token"
    data = {
        "grant_type": "client_credentials",
        "client_secret": secret,
        "client_id": id
    }
    moltin_login = requests.post(base_url, data=data)
    moltin_login.raise_for_status()

    return moltin_login.json()["access_token"]


def main():

    load_dotenv()

    moltin_id = os.getenv("MOLTIN_ID")
    moltin_secret = os.getenv("MOLTIN_SECRET")
    moltin_token = get_moltin_token(moltin_secret, moltin_id)
    
    # create_product(moltin_token)
    pprint(get_products(moltin_token))


if __name__ == "__main__":
    main()
