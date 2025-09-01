import requests

url = "https://convertor-pacote-agranel.fly.dev/conversao"

# Dados da requisição, AGORA INCLUINDO o campo "quantidade"
data = {
    "skuEmbalado": "2004",
    "quantidade": 1,  # Adicionamos a quantidade a ser convertida
    "skuAgranel": "203",
    "deposito": "Matriz"
}

print("Enviando requisição para:", url)
print("Com os dados:", data)

# Realiza a requisição POST com o JSON corrigido
response = requests.post(url, json=data)

print("\n--- Resultado ---")
print("Status Code:", response.status_code)

# Tenta decodificar a resposta como JSON, senão mostra o texto bruto
try:
    print("Resposta JSON:", response.json())
except Exception:
    print("Resposta (texto):", response.text)