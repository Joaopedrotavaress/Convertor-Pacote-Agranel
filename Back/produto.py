import requests;
from Back.Api import init_token, get_valid_token

import requests

BASE_URL = "https://api.bling.com.br/Api/v3"
ACCESS_TOKEN = get_valid_token()

def get_produtos_por_skus(skus):

    url = f"{BASE_URL}/produtos"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

 
    params = []
    for sku in skus:
        params.append(("codigos[]", sku))

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar produtos: {e}")
        return 