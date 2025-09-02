// api.js
export const API_BASE_URL = "https://convertor-pacote-agranel.fly.dev";

export async function converterProduto({ skuEmbalado, skuAgranel, deposito, quantidade }) {
  try {
    const res = await fetch(`${API_BASE_URL}/conversao`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skuEmbalado, skuAgranel, deposito, quantidade }),
    });

    const data = await res.json();

    if (data.error) {
      return { success: false, error: data.error };
    }

    if (!data.mensagem) {
      return { success: false, error: "Resposta inesperada da API" };
    }

    return { success: true, mensagem: data.mensagem };
  } catch (err) {
    return { success: false, error: err.message };
  }

}
export async function buscarProduto(sku) {
  try {
    const res = await fetch(`${API_BASE_URL}/produtos?skus=${sku}`);
    const data = await res.json();

    if (data.error) {
      return { success: false, error: data.error };
    }

    return { success: true, produtos: data.data };
  } catch (err) {
    return { success: false, error: err.message };
  }
}