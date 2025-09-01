from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

TOKEN_FILE = "token.json"

app = FastAPI(title="Conversor Pacote → Agranel")

# 🔹 Configuração de CORS
origins = [
    "http://localhost:3000",               # Front em dev
    "https://seu-front-no-vercel.vercel.app"  # Front em produção no Vercel
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
    quantidade: int   # 🔹 Obrigatório
    skuAgranel: str
    deposito: str

def obter_token():
    """
    Obtém um token de acesso válido.
    """
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
        
        # Salva os tokens no arquivo pela primeira vez
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)

    # 🔹 Simulação de validação (aqui poderia entrar sua função real `get_valid_token`)
    return token_data["access_token"]

@app.post("/conversao")
def conversao(request: ConversaoRequest):
    """
    Endpoint para realizar a conversão de um produto embalado para agranel.
    """
    try:
        access_token = obter_token()
    except Exception as e:
        return {"error": f"Erro ao obter token: {str(e)}"}

    try:
        # 🔹 Aqui seria chamada real da API Bling
        produtos = [
            {"codigo": request.skuEmbalado, "nome": "Produto Embalado Exemplo"},
            {"codigo": request.skuAgranel, "nome": "Produto Agranel Exemplo"},
        ]
    except Exception as e:
        return {"error": f"Erro ao buscar produtos: {str(e)}"}

    produto_embalado = next((p for p in produtos if p["codigo"] == request.skuEmbalado), None)
    produto_agranel = next((p for p in produtos if p["codigo"] == request.skuAgranel), None)

    if not produto_embalado or not produto_agranel:
        return {"error": "Produtos não encontrados"}

    try:
        # 🔹 Aqui entraria a lógica de movimentação real
        print(
            f"Movimentando {request.quantidade} de "
            f"{produto_embalado['nome']} → {produto_agranel['nome']} "
            f"no depósito {request.deposito} com token {access_token}"
        )
    except Exception as e:
        return {"error": f"Erro ao movimentar produtos: {str(e)}"}

    return {"mensagem": "Conversão realizada com sucesso!"}
