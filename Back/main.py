from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

# Importações do projeto
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
from .Api import get_valid_token, init_token


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

TOKEN_FILE = "/etc/secrets/token.json"

app = FastAPI(title="Conversor Pacote → Agranel")

# 🔹 Configuração de CORS
origins = [
    "http://localhost:3000",                 # Front em dev
    "https://seu-front-no-vercel.vercel.app" # Front em produção no Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de dados para a requisição
class ConversaoRequest(BaseModel):
    skuEmbalado: str
    quantidade: int   # 🔹 Obrigatório (pacotes embalados a converter)
    skuAgranel: str
    deposito: str

def obter_token():
    """
    Obtém um token de acesso válido, gerando um novo se necessário.
    """
    try:
        return get_valid_token()
    except Exception:
        AUTH_CODE = os.getenv("AUTH_CODE")
        if not AUTH_CODE:
            raise Exception("Nenhum token válido e AUTH_CODE não configurado.")
        return init_token(AUTH_CODE)

@app.post("/conversao")
def conversao(request: ConversaoRequest):
    """
    Endpoint para realizar a conversão de um produto embalado para agranel.
    """
    try:
        access_token = obter_token()
    except Exception as e:
        return {"error": str(e)}

    # 1) Buscar produtos reais no Bling
    try:
        produtos = get_produtos_por_skus(
            [request.skuEmbalado, request.skuAgranel],
            access_token
        )
    except Exception as e:
        return {"error": f"Erro ao buscar produtos no Bling: {str(e)}"}

    produto_embalado = next((p for p in produtos if p["codigo"] == request.skuEmbalado), None)
    produto_agranel = next((p for p in produtos if p["codigo"] == request.skuAgranel), None)

    if not produto_embalado or not produto_agranel:
        return {"error": "Produtos não encontrados no Bling"}

    # 2) Movimentar estoque
    try:
        for _ in range(request.quantidade):
            movimentar_produto_agranel(produto_embalado, produto_agranel, request.deposito, access_token)
    except Exception as e:
        return {"error": f"Erro ao movimentar produtos: {str(e)}"}

    return {"mensagem": "Conversão realizada com sucesso!"}
