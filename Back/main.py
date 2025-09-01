from fastapi import FastAPI
from pydantic import BaseModel
from .Api import get_valid_token, init_token, refresh_access_token
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
import os
import json
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
TOKEN_FILE = "token.json"

app = FastAPI(title="Conversor Pacote → Agranel")

# ----------------- CORS -----------------
origins = [
    "http://localhost:3000",
    "https://seu-site-no-vercel-ou-dominio.com"  # substitua pelo seu deploy
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Pydantic -----------------
class ConversaoRequest(BaseModel):
    skuEmbalado: str
    skuAgranel: str
    deposito: str

# ----------------- Função Token -----------------
def obter_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
    except FileNotFoundError:
        token_data = {
            "access_token": os.getenv("ACCESS_TOKEN"),
            "refresh_token": os.getenv("REFRESH_TOKEN"),
        }
        if not token_data["access_token"] or not token_data["refresh_token"]:
            raise Exception("Tokens não encontrados nas variáveis de ambiente")
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)

    # Verifica se o token expirou
    try:
        return get_valid_token(token_data)
    except Exception:
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            raise Exception("Refresh token não disponível")
        new_token_data = refresh_access_token(refresh_token)
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_token_data, f)
        return new_token_data["access_token"]

# ----------------- Endpoint -----------------
@app.post("/conversao")
def conversao(request: ConversaoRequest):
    try:
        access_token = obter_token()
    except Exception as e:
        return {"error": f"Erro ao obter token: {str(e)}"}

    try:
        produtos = get_produtos_por_skus([request.skuEmbalado, request.skuAgranel], access_token)
    except Exception as e:
        return {"error": f"Erro ao buscar produtos: {str(e)}"}

    produto_embalado = next((p for p in produtos if p["codigo"] == request.skuEmbalado), None)
    produto_agranel = next((p for p in produtos if p["codigo"] == request.skuAgranel), None)

    if not produto_embalado or not produto_agranel:
        return {"error": "Produtos não encontrados"}

    try:
        movimentar_produto_agranel(produto_embalado, produto_agranel, request.deposito, access_token)
    except Exception as e:
        return {"error": f"Erro ao movimentar produtos: {str(e)}"}

    return {"mensagem": "Conversão realizada com sucesso!"}
