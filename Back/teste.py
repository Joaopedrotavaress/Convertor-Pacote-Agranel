from Api import get_valid_token, init_token
from produto import get_produtos_por_skus
from estoque import movimentar_produto_agranel
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

    # ---------- PEGAR PRODUTOS ----------
    skus_teste = ["2004", "203"]  # 2004 pacote, 203 agranel
    produtos = get_produtos_por_skus(skus_teste, access_token)

    produto_embalado = None
    produto_agranel = None

    for p in produtos:
        if p.get("codigo") == "2004":
            produto_embalado = p
        elif p.get("codigo") == "203":
            produto_agranel = p

    if not produto_embalado or not produto_agranel:
        print("❌ Não foi possível localizar os produtos para o teste")
    else:

        # Exemplo de teste: mover do pacote para o agranel no depósito "Matriz"
        movimentar_produto_agranel(produto_embalado, produto_agranel, "Matriz", access_token)
