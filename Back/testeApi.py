import requests

url = "https://convertor-pacote-agranel.onrender.com/conversao"

data = {
    "skuEmbalado": "2004",
    "skuAgranel": "203",
    "deposito": "Matriz"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())