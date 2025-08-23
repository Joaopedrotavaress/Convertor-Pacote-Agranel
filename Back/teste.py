from Api import get_valid_token, init_token
from produto import get_produtos_por_skus
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # ---------- PEGAR OU GERAR TOKEN ----------
    try:
        access_token = get_valid_token()
        print("✅ Token carregado do token.json")
    except Exception:
        AUTH_CODE = os.getenv("AUTH_CODE")  
        access_token = init_token(AUTH_CODE)
        print("✅ Novo token gerado e salvo no token.json")

    # ---------- TESTE DE PRODUTOS ----------
    skus_teste = ["2004", "201"]
    produtos = get_produtos_por_skus(skus_teste, access_token)

    if produtos:
        print("✅ Produtos encontrados:")
        for p in produtos:
            print(f"- {p.get('nome')} (SKU: {p.get('codigo')} (ID: {p.get('id')}))")
    else:
        print("⚠️ Nenhum produto encontrado para os SKUs informados.")
