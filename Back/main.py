from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv
from typing import List

# Importações do projeto (relativas, com ponto)
from .produto import get_produtos_por_skus
from .estoque import movimentar_produto_agranel
from .Api import get_valid_token, init_token

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = FastAPI(title="Conversor Pacote → Agranel")

# --- Configuração de CORS (Cross-Origin Resource Sharing) ---
# Permite que seu frontend Vercel se comunique com esta API
origins = [
    "http://localhost:3000",                   # Para desenvolvimento local do frontend
    "https://convertor-pacote-agranel.vercel.app", # URL de produção do seu frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Permite URLs de preview da Vercel (ex: nome-do-projeto-git-main-sua-conta.vercel.app)
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Dados ---
class ConversaoRequest(BaseModel):
    skuEmbalado: str
    quantidade: int = 1
    skuAgranel: str
    deposito: str

# --- Funções Auxiliares ---
def obter_token():
    """
    Obtém um token de acesso válido, gerando um novo se o atual não existir.
    """
    try:
        return get_valid_token()
    except Exception as e:
        # Tenta gerar um novo token apenas se o erro for "nenhum token encontrado"
        if "Nenhum token encontrado" in str(e):
            AUTH_CODE = os.getenv("AUTH_CODE")
            if not AUTH_CODE:
                raise Exception("Nenhum token válido e AUTH_CODE não configurado.")
            return init_token(AUTH_CODE)
        # Se o erro for outro (ex: refresh token inválido), propaga a exceção
        raise

async def processar_conversoes_em_background(
    produto_embalado: dict,
    produto_agranel: dict,
    deposito: str,
    access_token: str,
    quantidade: int
):
    """
    Executa a movimentação de estoque em segundo plano, respeitando o limite da API.
    """
    print(f"Iniciando processamento em background de {quantidade} pacote(s)...")
    for i in range(quantidade):
        print(f"Processando pacote {i + 1} de {quantidade}...")
        # Executa a função síncrona (que faz chamadas de rede) em uma thread separada
        # para não bloquear o servidor principal.
        await asyncio.to_thread(
            movimentar_produto_agranel,
            produto_embalado,
            produto_agranel,
            deposito,
            access_token
        )
        # Pausa para garantir que não excedamos 3 requisições por segundo.
        # A função movimentar_produto_agranel faz 3 requisições, então esperamos 1 segundo
        # entre o processamento de cada pacote.
        await asyncio.sleep(1)
    print("Processamento em background concluído.")


# --- Endpoint Principal ---
@app.post("/conversao")
async def conversao(request: ConversaoRequest, background_tasks: BackgroundTasks):
    """
    Endpoint que valida os produtos e inicia a conversão em background,
    retornando uma resposta imediata ao usuário.
    """
    try:
        access_token = obter_token()
    except Exception as e:
        return {"error": str(e)}

    # 1) Validação inicial: Buscar produtos no Bling
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

    # 2) Agendar a tarefa demorada para ser executada em segundo plano
    background_tasks.add_task(
        processar_conversoes_em_background,
        produto_embalado,
        produto_agranel,
        request.deposito,
        access_token,
        request.quantidade
    )

    # 3) Retornar uma resposta imediata ao usuário
    return {"mensagem": f"Conversão de {request.quantidade} pacote(s) iniciada com sucesso. O processo continuará em segundo plano."}
@app.get("/produtos")
async def consultar_produtos(skus: List[str] = Query(...)):
    """
    Consulta informações de produtos por SKUs e retorna os detalhes.
    """
    try:
        access_token = obter_token()
        produtos = get_produtos_por_skus(skus, access_token)
        if not produtos:
            return {"error": "Nenhum produto encontrado"}
        return {"data": produtos}
    except Exception as e:
        return {"error": str(e)}