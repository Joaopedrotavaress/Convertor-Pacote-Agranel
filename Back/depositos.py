import requests
BASE_URL = "https://api.bling.com.br/Api/v3"
def get_depositos(access_token):
    url = f"{BASE_URL}/depositos"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # imprime JSON completo para inspeção
        import json
        print("🔹 JSON completo de depósitos:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar depósitos: {e}")
        return []
