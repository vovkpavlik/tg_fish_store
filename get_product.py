import requests


def get_products(access_token):
    base_url = "https://api.moltin.com/pcm/products"
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    list_products = requests.get(base_url, headers=headers)
    list_products.raise_for_status

    return list_products.json()