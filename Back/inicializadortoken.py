from Api import init_token
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    AUTH_CODE = os.getenv("AUTH_CODE")

    if not AUTH_CODE:
        raise ValueError("❌ AUTH_CODE não definido no .env")

    print("🔄 Iniciando fluxo init_token com AUTH_CODE...")
    token = init_token(AUTH_CODE)
    print(f"✅ Novo Access Token: {token}")
