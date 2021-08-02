import requests

from pprint import pprint


def get_img_url(access_token, img_id):
    base_url = "https://api.moltin.com/v2/files/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    img_info = requests.get(f"{base_url}{img_id}", headers=headers)
    img_info.raise_for_status()

    return img_info.json()["data"]["link"]["href"]


def get_product_info(access_token, product_id):
    base_url = "https://api.moltin.com/v2/products/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    product_info = requests.get(f"{base_url}{product_id}", headers=headers)
    product_info.raise_for_status()

    return product_info.json()["data"]


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
        "grant_type": "client_credentials",
        "client_secret": secret,
        "client_id": id      
    }

    moltin_login = requests.post(base_url, data=data)
    # pprint(moltin_login.json())
    moltin_login.raise_for_status()

    return moltin_login.json()["access_token"]


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
    

def create_customer(access_token, user_id, user_email):
    base_url = "https://api.moltin.com/v2/customers"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "data": {
            "type": "customer",
            "name": f"customer_{user_id}",
            "email": user_email,
            "password": str(user_id)
        }
    } 

    response = requests.post(base_url, headers=headers, json=data)
    response.raise_for_status()
