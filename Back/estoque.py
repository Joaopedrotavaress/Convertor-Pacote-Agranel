import requests
import math
# IDs dos depósitos atuais
DEPOSITO_CEU_AZUL = 14887449554
DEPOSITO_MATRIZ = 5196687625
DEPOSITO_RIO_BRANCO = 14887449552
DEPOSITO_SAO_BENEDITO = 14887449555

BASE_URL = "https://api.bling.com.br/Api/v3"

def get_produtos_kg(produto_id, access_token):
    url = f"{BASE_URL}/produtos/{produto_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "data" in data:
            return data["data"].get("pesoLiquido", None)
        else:
            produtos = data.get("retorno", {}).get("produtos", [])
            if produtos:
                return produtos[0].get("produto", {}).get("pesoLiquido", None)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar produto pelo ID: {e}")
        return None

def movimentar_produto_agranel(produto_embalado_json, produto_agranel_json, nome_deposito, access_token):
    # Mapear depósitos
    depositos = {
        "Céu Azul": DEPOSITO_CEU_AZUL,
        "Matriz": DEPOSITO_MATRIZ,
        "Rio Branco": DEPOSITO_RIO_BRANCO,
        "São Benedito": DEPOSITO_SAO_BENEDITO
    }
    deposito_id = depositos.get(nome_deposito)
    if not deposito_id:
        print(f"❌ Depósito '{nome_deposito}' não encontrado")
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # --- 1) Baixa do produto embalado ---
    payload_saida = {
        "produto": {"id": produto_embalado_json.get("id")},
        "deposito": {"id": deposito_id},
        "operacao": "S",  # Saída
        "quantidade": 1,  # sempre 1 pacote
        "preco": produto_embalado_json.get("preco", 0),
        "custo": produto_embalado_json.get("fornecedor", {}).get("precoCusto", 0),
        "observacoes": "Conversão para estoque a granel"
    }

    try:
        response_saida = requests.post(f"{BASE_URL}/estoques", headers=headers, json=payload_saida)
        response_saida.raise_for_status()
        print("✅ Produto embalado baixado com sucesso")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao dar baixa no produto embalado: {e}")
        return None

    # --- 2) Entrada no produto a granel ---
    peso_liquido = get_produtos_kg(produto_embalado_json.get("id"), access_token)
    peso_liquido = math.floor(peso_liquido)

    payload_entrada = {
        "produto": {"id": produto_agranel_json.get("id")},
        "deposito": {"id": deposito_id},
        "operacao": "E",  # Entrada
        "quantidade": peso_liquido,
        "preco": produto_agranel_json.get("preco", produto_embalado_json.get("preco", 0)),
        "custo": produto_agranel_json.get("fornecedor", {}).get("precoCusto",
                 produto_embalado_json.get("fornecedor", {}).get("precoCusto", 0)),
        "observacoes": "Entrada do peso convertido do pacote"
    }

    try:
        response_entrada = requests.post(f"{BASE_URL}/estoques", headers=headers, json=payload_entrada)
        response_entrada.raise_for_status()
        print("✅ Produto a granel registrado com sucesso")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao adicionar produto a granel: {e}")
        return None
