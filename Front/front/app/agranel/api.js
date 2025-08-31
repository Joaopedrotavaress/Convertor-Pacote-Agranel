// api.js
export const API_BASE_URL = "https://convertor-pacote-agranel.onrender.com";

export async function converterProduto({ skuEmbalado, skuAgranel, deposito }) {
  try {
    const res = await fetch(`${API_BASE_URL}/conversao`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skuEmbalado, skuAgranel, deposito }),
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Erro desconhecido");
    return { success: true, mensagem: data.mensagem };
  } catch (err) {
    return { success: false, error: err.message };
  }
}
