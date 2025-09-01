from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys  # Importado para depuração
# Importando o módulo Api inteiro para clareza
from . import Api 
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
from fastapi.middleware.cors import CORSMiddleware

# --- Depuração de Inicialização ---
# Esta mensagem aparecerá nos logs do Render se o arquivo for lido.
print("✅ Arquivo main.py iniciado com sucesso.", file=sys.stderr)

app = FastAPI(title="Conversor Pacote → Agranel")

# ----------------- CORS -----------------

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

# ----------------- Endpoint de Verificação de Saúde -----------------
@app.get("/health")
def health_check():
    """
    Um endpoint simples para verificar se a API está no ar e respondendo,
    sem precisar de autenticação.
    """
    return {"status": "ok"}

# ----------------- Função Token (SIMPLIFICADA) -----------------
def obter_token():
    """
    Delega toda a lógica de obtenção e renovação de token para o módulo Api.
    """
    try:
        print("➡️  Tentando obter o token da API externa...", file=sys.stderr)
        token = Api.get_valid_token()
        print("✅ Token obtido com sucesso.", file=sys.stderr)
        return token
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao obter token: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=503,
            detail=f"Erro de autenticação com a API externa: {e}"
        )

# ----------------- Endpoint Principal -----------------
@app.post("/conversao")
def conversao(request: ConversaoRequest):
    print("➡️  Requisição recebida em /conversao.", file=sys.stderr)
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

