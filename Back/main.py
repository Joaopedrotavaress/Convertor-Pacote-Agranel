from fastapi import FastAPI
from pydantic import BaseModel
# Supondo que estes imports venham de arquivos locais na sua estrutura de projeto
# from .Api import get_valid_token, refresh_access_token
# from .produto import get_produtos_por_skus
# from .estoque import movimentar_produto_agranel
import os
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

TOKEN_FILE = "token.json"

app = FastAPI(title="Conversor Pacote → Agranel")

# Modelo de dados para a requisição
class ConversaoRequest(BaseModel):
    skuEmbalado: str
    quantidade: int # Adicionado para especificar a quantidade a ser convertida
    skuAgranel: str
    deposito: str

def obter_token():
    """
    Obtém um token de acesso válido.
    Lê o token de um arquivo, ou das variáveis de ambiente se o arquivo não existir.
    Atualiza o token se ele estiver expirado.
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

    # Verifica se o token expirou e faz refresh se necessário
    try:
        # Aqui você teria uma função que valida o token, por exemplo, verificando a data de expiração
        # Para este exemplo, vamos simular que get_valid_token lança uma exceção se inválido
        # return get_valid_token(token_data) 
        return token_data["access_token"] # Retorno simplificado
    except Exception:
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            raise Exception("Refresh token não disponível")
        
        # new_token_data = refresh_access_token(refresh_token)
        # Comentei a linha acima porque a função não foi fornecida
        # Simulando uma resposta de novos tokens
        new_token_data = {
            "access_token": "new_access_token_from_refresh",
            "refresh_token": "new_refresh_token_optional"
        }

        with open(TOKEN_FILE, "w") as f:
            json.dump(new_token_data, f)
        
        return new_token_data["access_token"]

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
        # produtos = get_produtos_por_skus([request.skuEmbalado, request.skuAgranel], access_token)
        # Comentei a linha acima porque a função não foi fornecida
        # Simulando uma resposta da busca de produtos
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
        # movimentar_produto_agranel(produto_embalado, produto_agranel, request.deposito, access_token)
        # Comentei a linha acima porque a função não foi fornecida
        print(f"Movimentando {request.quantidade} de {produto_embalado['nome']} para {produto_agranel['nome']} no depósito {request.deposito}")
    except Exception as e:
        return {"error": f"Erro ao movimentar produtos: {str(e)}"}

    return {"mensagem": "Conversão realizada com sucesso!"}
