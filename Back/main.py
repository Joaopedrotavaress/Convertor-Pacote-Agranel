from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# Importando o módulo Api inteiro para clareza
from . import Api 
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Conversor Pacote → Agranel")

# ----------------- CORS -----------------
origins = [
    "http://localhost:3000",  # Endereço comum para desenvolvimento com React, Vue, etc.
    "http://127.0.0.1:3000", # Outro endereço comum para desenvolvimento local.
    "https://seu-frontend-no-vercel.com", # IMPORTANTE: Substitua pela URL do seu site em produção.
    # Adicione aqui outras URLs que precisam de acesso.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,       # Permite o envio de cookies/autenticação.
    allow_methods=["*"],          # Permite todos os métodos (GET, POST, PUT, etc.).
    allow_headers=["*"],          # Permite todos os cabeçalhos nas requisições.
)

# ----------------- Pydantic -----------------
class ConversaoRequest(BaseModel):
    skuEmbalado: str
    quantidade: int
    skuAgranel: str
    deposito: str

# ----------------- Função Token (SIMPLIFICADA) -----------------
def obter_token():
    """
    Delega toda a lógica de obtenção e renovação de token para o módulo Api.
    """
    try:
        # A única chamada necessária. O Api.py cuida do resto.
        return Api.get_valid_token()
    except Exception as e:

        raise HTTPException(
            status_code=503, # 503 Service Unavailable é ideal para falhas com serviços externos.
            detail=f"Erro de autenticação com a API externa: {e}"
        )

# ----------------- Endpoint -----------------
@app.post("/conversao")
def conversao(request: ConversaoRequest):
    # A obtenção do token agora é limpa e segura.
    access_token = obter_token()

    try:
        produtos = get_produtos_por_skus(
            [request.skuEmbalado, request.skuAgranel], 
            access_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

    produto_embalado = next((p for p in produtos if p.get("codigo") == request.skuEmbalado), None)
    produto_agranel = next((p for p in produtos if p.get("codigo") == request.skuAgranel), None)

    if not produto_embalado or not produto_agranel:
        raise HTTPException(status_code=404, detail="Um ou mais SKUs não foram encontrados.")

    try:
        movimentar_produto_agranel(
            produto_embalado,
            produto_agranel,
            request.quantidade,
            request.deposito,
            access_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao movimentar produtos: {str(e)}")

    return {"mensagem": "Conversão realizada com sucesso!"}
