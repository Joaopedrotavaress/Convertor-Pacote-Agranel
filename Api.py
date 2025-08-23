import requests;
import base64;
import json;
import time;

CLIENT_ID = '7769a0b07187acd7729185588c4e66f63528e5e0'
CLIENT_SECRET  = '7bc9a5a38b712d21a8ff946a0288aa6955bf4b11f4b52bf3685dd5c76c1e'
REDIRECT_URI = 'http://localhost:3000/callback'
TOKEN_FILE = "token.json"


def save_token(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)

def load_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def init_token(auth_code):
    token_data = get_access_token(auth_code)
    token_data["expires_at"] = time.time() + token_data["expires_in"]
    save_token(token_data)
    return token_data["access_token"]


def get_valid_token():
    token_data = load_token()
    if not token_data:
        raise Exception("Nenhum token encontrado. Inicialize com Auth Code.")

    if time.time() > token_data["expires_at"]:
        token_data = refresh_access_token(token_data["refresh_token"])
        token_data["expires_at"] = time.time() + token_data["expires_in"]
        save_token(token_data)

    return token_data["access_token"]

def get_access_token(auth_code):
    url = "https://api.bling.com.br/Api/v3/oauth/token"

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json()

def refresh_access_token(refresh_token):
    url = "https://api.bling.com.br/Api/v3/oauth/token"

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, headers=headers, data=data)
    token_data = response.json()

    
    if "access_token" in token_data:
        
        token_data["expires_at"] = time.time() + token_data["expires_in"]
        
        save_token(token_data)
        print("Access Token atualizado automaticamente.")
        return token_data
    else:
       
        raise Exception(
            "Refresh Token expirou ou é inválido. Solicite novo Auth Code ao administrador."
        )
