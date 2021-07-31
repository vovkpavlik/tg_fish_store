import os

import requests


def add_to_cart(access_token, id, sku, quantity):    
    base_url = f"https://api.moltin.com/v2/carts/{id}/items"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "data": {
            "quantity": quantity,
            "type": "cart_item",
            "sku": sku,
        }
    }

    add_to_cart = requests.post(base_url, headers=headers, json=data)
    add_to_cart.raise_for_status()


def get_cart_info(access_token, cart_id):
    base_url = f"https://api.moltin.com/v2/carts/{cart_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(base_url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]


def get_cart_items(access_token, cart_id):
    base_url = f"https://api.moltin.com/v2/carts/{cart_id}/items"
    
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

    return response.json()["data"]


def delete_cart_item(access_token, cart_id, product_id):
    base_url = f"https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.delete(base_url, headers=headers)
    response.raise_for_status()
    