import requests

url = "https://convertor-pacote-agranel.onrender.com/conversao"

data = {
    "skuEmbalado": "2004",
    "skuAgranel": "203",
    "deposito": "Matriz"
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
try:
    print("Resposta JSON:", response.json())
except Exception:
    print("Resposta bruta:", response.text)
