from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# Importando o módulo Api inteiro para clareza
from . import Api 
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Conversor Pacote → Agranel")

# ----------------- CORS -----------------
# (Seu código CORS permanece o mesmo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://seu-site-no-vercel-ou-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        # Usando HTTPException para retornar um erro HTTP adequado.
        # Isso dá mais informações ao frontend sobre o que aconteceu.
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

