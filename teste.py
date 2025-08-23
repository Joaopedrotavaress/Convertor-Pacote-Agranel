from Api import get_valid_token
from produto import get_produtos_por_skus  # supondo que você salvou em produto.py
import json

if __name__ == "__main__":
    try:
        # Teste: pegar produtos por SKUs existentes
        skus_teste = ["2004", "201"]  # substitua por SKUs válidos do seu Bling
        produtos = get_produtos_por_skus(skus_teste)

        if produtos:
            print("✅ Produtos encontrados:")
            for p in produtos:
                print(f"- {p.get('nome')} (SKU: {p.get('codigo')} (ID: {p.get('id')}))")

           
        else:
            print("⚠️ Nenhum produto encontrado para os SKUs informados.")

    except Exception as e:
        print(f"❌ Erro ao rodar teste: {e}")
