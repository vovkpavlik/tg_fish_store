import requests


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
        "client_id": id,
        "client_secret": secret,
        "grant_type": "client_credentials"
    }

    moltin_login = requests.post(base_url, data=data)
    moltin_login.raise_for_status()

    return moltin_login.json()["access_token"]
