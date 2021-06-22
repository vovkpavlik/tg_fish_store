import requests


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
