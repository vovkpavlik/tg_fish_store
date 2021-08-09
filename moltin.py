import requests


def get_img_url(access_token, img_id):
    base_url = "https://api.moltin.com/v2/files/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    img = requests.get(f"{base_url}{img_id}", headers=headers)
    img.raise_for_status()

    return img.json()["data"]["link"]["href"]


def get_product_info(access_token, product_id):
    base_url = "https://api.moltin.com/v2/products/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    product = requests.get(f"{base_url}{product_id}", headers=headers)
    product.raise_for_status()

    return product.json()["data"]


def get_products(access_token):
    base_url = "https://api.moltin.com/v2/products"
    headers = {
        "Authorization": access_token,
    }
    products = requests.get(base_url, headers=headers)
    products.raise_for_status()

    return products.json()


def get_moltin_token(secret, moltin_id):
    base_url = "https://api.moltin.com/oauth/access_token"
    
    data = {
        "grant_type": "client_credentials",
        "client_secret": secret,
        "client_id": moltin_id      
    }

    response = requests.post(base_url, data=data)
    response.raise_for_status()
    
    token = response.json()["access_token"]
    token_time = response.json()["expires_in"]
       
    return token, token_time


def get_actual_token(redis, moltin_secret, moltin_id):  
    token = redis.get("moltin_token")
    if not token:
        token, token_time = get_moltin_token(moltin_secret, moltin_id)
        redis.set("moltin_token", token, ex=token_time-10)
    
    return token


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

    response = requests.post(base_url, headers=headers, json=data)
    response.raise_for_status()


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
