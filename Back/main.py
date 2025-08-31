from fastapi import FastAPI
from pydantic import BaseModel
from Api import get_valid_token, init_token
from produto import get_produtos_por_skus
from estoque import movimentar_produto_agranel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Conversor Pacote → Agranel")

class ConversaoRequest(BaseModel):
    skuEmbalado: str
    skuAgranel: str
    deposito: str

def obter_token():
    """
    Garante que sempre teremos um token válido
    """
    try:
        return get_valid_token() 
    except Exception:
        AUTH_CODE = os.getenv("AUTH_CODE")
        if not AUTH_CODE:
            raise Exception("AUTH_CODE não definido nas variáveis de ambiente")
        return init_token(AUTH_CODE)  

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
