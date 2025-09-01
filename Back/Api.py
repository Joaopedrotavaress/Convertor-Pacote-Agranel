import requests
import base64
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Usando o caminho do disco persistente
TOKEN_FILE = "/etc/secrets/token.json"

# ----------------- Utilidades -----------------
def save_token(token_data: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2, ensure_ascii=False)

def load_token() -> dict | None:
    try:
        with open(TOKEN_FILE, "r") as f:
            print("✅ Token carregado do arquivo token.json no disco persistente")
            return json.load(f)
    except FileNotFoundError:
        token_env = os.getenv("TOKEN_JSON")
        if token_env:
            print("✅ Token carregado da variável de ambiente TOKEN_JSON (carga inicial)")
            token_data = json.loads(token_env)
            return token_data
        print("⚠️ Nenhum token encontrado (nem arquivo, nem variável de ambiente).")
        return None

def _auth_header():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

# ----------------- Fluxo de Autenticação -----------------
def init_token(auth_code: str) -> str:
    url = "https://api.bling.com.br/Api/v3/oauth/token"
    headers = _auth_header() | {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        print("❌ Erro ao inicializar token:", resp.text)
        raise Exception(f"{resp.status_code} - {resp.text}")
    token_data = resp.json()
    token_data["expires_at"] = time.time() + token_data["expires_in"]
    save_token(token_data)
    print("✅ Token inicializado com sucesso.")
    return token_data["access_token"]

def refresh_access_token(refresh_token: str) -> dict:
    url = "https://api.bling.com.br/Api/v3/oauth/token"
    headers = _auth_header() | {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        print("❌ Erro ao renovar token:", resp.text)
        raise Exception(f"{resp.status_code} - {resp.text}")
    token_data = resp.json()
    token_data["expires_at"] = time.time() + token_data["expires_in"]
    save_token(token_data)
    print("✅ Access Token atualizado com sucesso.")
    return token_data

def get_valid_token() -> str:
    token_data = load_token()
    
    # --- LINHAS ADICIONADAS PARA IMPRIMIR O TOKEN ---
    print("\n--- INÍCIO: DADOS DO TOKEN CARREGADO ---")
    if token_data:
        # Imprime o JSON de forma legível
        print(json.dumps(token_data, indent=2, ensure_ascii=False))
    else:
        print("Nenhum dado de token para exibir.")
    print("--- FIM: DADOS DO TOKEN CARREGADO ---\n")
    # --- FIM DAS LINHAS ADICIONADAS ---

    if not token_data:
        raise Exception("Nenhum token encontrado. Rode init_token(auth_code) primeiro.")

    if time.time() > token_data.get("expires_at", 0):
        print("⚠️ Token expirado, tentando renovar...")
        try:
            token_data = refresh_access_token(token_data["refresh_token"])
        except Exception as e:
            raise Exception("❌ Refresh token inválido ou expirado. "
                            "Gere um novo authorization_code no Bling e rode init_token(auth_code).") from e

    return token_data["access_token"]