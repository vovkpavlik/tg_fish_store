import os

import requests
from dotenv import load_dotenv
from pprint import pprint


def delete_product(access_token):
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    response = requests.delete('https://api.moltin.com/v2/products/bc72b5b8-dce6-4a45-ae82-c6d7ec77e650', headers=headers)


def get_products_id(products):
    products_id = [product["id"] for product in products["data"]]    
    return products_id


def get_products_title(products):
    products_title = [product["name"] for product in products["data"]]    
    return products_title



def update_products(access_token, products_id):
    base_url = "https://api.moltin.com/v2/products/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    for product_id in products_id:
        data = {
            "data": {
                "id": product_id,
                "manage_stock": False,
                "type": "product"
            }
        }

        response = requests.put(f"{base_url}{product_id}", headers=headers, json=data)
        response.raise_for_status()


def create_product(access_token):
    base_url = "https://api.moltin.com/v2/products"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "type": "product",
            "name": "Dolphin",
            "slug": "dolphin",
            "sku": "dolphin",
            "manage_stock": True,
            "description": "Do not eat!",
            "price": [
                {
                    "amount": 200000,
                    "currency": "USD",
                    "includes_tax": True
                }
            ],
            "commodity_type": "physical",
            "status": "live"
        }
    }

    add_new_product = requests.post(base_url, headers=headers, json=data)
    add_new_product.raise_for_status()


def get_products(access_token):
    base_url = "https://api.moltin.com/v2/products"
    headers = {
        "Authorization": access_token,
    }
    list_products = requests.get(base_url, headers=headers)
    list_products.raise_for_status()

    return list_products.json()


def get_moltin_token(secret, id):
    base_url = "https://api.moltin.com/oauth/access_token"
    data = {
        "client_id": id,
        "client_secret": secret,
        "grant_type": "client_credentials"
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
    # delete_product(moltin_token)
    # products_id = get_products_id(get_products(moltin_token))
    # update_products(moltin_token, products_id)
    print(get_products_title(get_products(moltin_token)))
    # pprint(get_products(moltin_token))


if __name__ == "__main__":
    main()
