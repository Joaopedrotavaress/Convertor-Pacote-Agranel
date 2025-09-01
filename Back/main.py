from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from . import Api
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
from fastapi.middleware.cors import CORSMiddleware

# --- Depuração de Inicialização ---
# Esta mensagem aparecerá nos logs do Render se o ficheiro for lido com sucesso.
print("✅ Arquivo main.py iniciado com sucesso.", file=sys.stderr)

app = FastAPI(title="Conversor Pacote → Agranel")

# ----------------- CORS -----------------
# Configuração para permitir que o seu frontend se comunique com esta API.
# Em produção, é recomendado substituir "*" por a URL exata do seu frontend.
origins = ["*"]

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

# ----------------- Endpoint de Verificação de Saúde -----------------
@app.get("/health")
def health_check():
    """
    Endpoint simples para verificar se a API está no ar e a responder.
    Útil para monitorização.
    """
    return {"status": "ok"}

# ----------------- Função Auxiliar para Token -----------------
def obter_token_valido():
    """
    Delega toda a lógica de obtenção e renovação de token para o módulo Api.
    Centraliza o tratamento de erros de autenticação.
    """
    try:
        print("➡️  Tentando obter o token da API externa...", file=sys.stderr)
        token = Api.get_valid_token()
        print("✅ Token obtido com sucesso.", file=sys.stderr)
        return token
    except Exception as e:
        # Se a obtenção/renovação do token falhar, a API está efetivamente indisponível.
        print(f"❌ ERRO CRÍTICO ao obter token: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"Erro de autenticação com a API externa: {e}"
        )

# ----------------- Endpoint Principal da Conversão -----------------
@app.post("/conversao")
def conversao(request: ConversaoRequest):
    """
    Orquestra o processo de conversão:
    1. Obtém um token de acesso válido.
    2. Busca os dados dos produtos.
    3. Realiza a movimentação de estoque.
    """
    print(f"➡️  Requisição recebida para converter {request.quantidade}x SKU {request.skuEmbalado}...", file=sys.stderr)
    access_token = obter_token_valido()

    # --- 1. Buscar Produtos ---
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
        raise HTTPException(status_code=404, detail="Um ou mais SKUs não foram encontrados na API externa.")

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

