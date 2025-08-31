import requests

BASE_URL = "https://api.bling.com.br/Api/v3"

def get_produtos_por_skus(skus, access_token):
   
    url = f"{BASE_URL}/produtos"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    params = [("codigos[]", sku) for sku in skus]

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return []
    
def get_produtos_kg(produto_id, access_token):
    url = f"{BASE_URL}/produtos/{produto_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            return data["data"].get("pesoLiquido", None)
        else:
            produtos = data.get("retorno", {}).get("produtos", [])
            if produtos:
                return produtos[0].get("produto", {}).get("pesoLiquido", None)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar produto pelo ID: {e}")
        return None
