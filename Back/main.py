from fastapi import FastAPI
from pydantic import BaseModel
from Api import get_valid_token, init_token
from produto import get_produtos_por_skus
from estoque import movimentar_produto_agranel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class ConversaoRequest(BaseModel):
    skuEmbalado: str
    skuAgranel: str
    deposito: str

@app.post("/conversao")
def conversao(request: ConversaoRequest):
    try:
        access_token = get_valid_token()
    except:
        AUTH_CODE = os.getenv("AUTH_CODE")
        access_token = init_token(AUTH_CODE)

    produtos = get_produtos_por_skus([request.skuEmbalado, request.skuAgranel], access_token)

    produto_embalado = next((p for p in produtos if p["codigo"] == request.skuEmbalado), None)
    produto_agranel = next((p for p in produtos if p["codigo"] == request.skuAgranel), None)

    if not produto_embalado or not produto_agranel:
        return {"error": "Produtos não encontrados"}

    movimentar_produto_agranel(produto_embalado, produto_agranel, request.deposito, access_token)
    return {"mensagem": "Conversão realizada com sucesso!"}
