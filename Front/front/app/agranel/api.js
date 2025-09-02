// api.js
export const API_BASE_URL = "https://convertor-pacote-agranel.fly.dev"; // corrigido

export async function converterProduto({ skuEmbalado, skuAgranel, deposito }) {
  try {
    const res = await fetch(`${API_BASE_URL}/conversao`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skuEmbalado, quantidade, skuAgranel, deposito }), // agora inclui quantidade
    });

    if (!res.ok) {
      // Se não for 200, retorna erro mais claro
      const text = await res.text();
      return { success: false, error: `Erro ${res.status}: ${text}` };
    }

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
