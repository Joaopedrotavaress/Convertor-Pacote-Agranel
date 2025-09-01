from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import json

# Imports locais
from . import Api
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel

print("✅ Arquivo main.py iniciado com sucesso.", file=sys.stderr)

app = FastAPI(title="Conversor Pacote → Agranel")

# ----------------- CORS -----------------
origins = ["*"]  # Em produção, use apenas a URL do seu front
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Modelo de Dados de Entrada -----------------
class ConversaoRequest(BaseModel):
    skuEmbalado: str
    quantidade: int
    skuAgranel: str
    deposito: str

# ----------------- Endpoint de Verificação -----------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ----------------- Função Auxiliar para Token -----------------
def obter_token_valido() -> str:
    """
    Garante que o token de acesso seja uma string válida.
    """
    try:
        token = Api.get_valid_token()
        # Se retornar dicionário, extrair apenas o access_token
        if isinstance(token, dict):
            token = token.get("access_token")
        if not isinstance(token, str):
            raise Exception("Token inválido, esperado string")
        return token
    except Exception as e:
        print(f"❌ ERRO ao obter token: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=503,
            detail=f"Erro de autenticação com a API externa: {e}"
        )

# ----------------- Endpoint Principal -----------------
@app.post("/conversao")
def conversao(request: ConversaoRequest):
    print(f"➡️ Requisição recebida para converter {request.quantidade}x SKU {request.skuEmbalado}...", file=sys.stderr)
    access_token = obter_token_valido()
    print(f"➡️ Token usado: {access_token}", file=sys.stderr)

    # --- 1. Buscar Produtos ---
    try:
        produtos = get_produtos_por_skus([request.skuEmbalado, request.skuAgranel], access_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

    # Alguns endpoints da Bling retornam "produto": {...}, outros direto {...}
    def extrair_codigo(produto):
        if "codigo" in produto:
            return produto["codigo"]
        if "produto" in produto and "codigo" in produto["produto"]:
            return produto["produto"]["codigo"]
        return None

    produto_embalado = next((p for p in produtos if extrair_codigo(p) == request.skuEmbalado), None)
    produto_agranel = next((p for p in produtos if extrair_codigo(p) == request.skuAgranel), None)

    if not produto_embalado or not produto_agranel:
        raise HTTPException(status_code=404, detail="Um ou mais SKUs não foram encontrados na API externa.")

    # --- DEBUG: Log do payload ---
    payload_debug = {
        "produto_embalado": produto_embalado,
        "produto_agranel": produto_agranel,
        "quantidade": request.quantidade,
        "deposito": request.deposito
    }
    print("➡️ Payload que será enviado para Bling:", file=sys.stderr)
    print(json.dumps(payload_debug, indent=2, ensure_ascii=False), file=sys.stderr)

    # --- 2. Movimentar Estoque ---
    try:
        movimentar_produto_agranel(
            produto_embalado_json=produto_embalado,
            produto_agranel_json=produto_agranel,
            quantidade_pacotes=request.quantidade,
            nome_deposito=request.deposito,
            access_token=access_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao movimentar produtos: {str(e)}")

    print("✅ Conversão finalizada com sucesso.", file=sys.stderr)
    return {"mensagem": "Conversão realizada com sucesso!"}
