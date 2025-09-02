"use client";

import { useState } from "react";
import { FaBox, FaExchangeAlt, FaCheckCircle } from "react-icons/fa";
import Image from "next/image";
import { converterProduto, buscarProduto } from "./api";

// Tipagem para o produto retornado pela API
interface Produto {
  id?: string;
  codigo: string;
  nome: string;
  pesoLiquido?: number;
}

const Agranel: React.FC = () => {
  const [skuEmbalado, setSkuEmbalado] = useState("");
  const [skuAgranel, setSkuAgranel] = useState("");
  const [deposito, setDeposito] = useState("Matriz");
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState<string | null>(null);

  const [produtoEmbaladoInfo, setProdutoEmbaladoInfo] = useState<Produto | null>(null);
  const [produtoAgranelInfo, setProdutoAgranelInfo] = useState<Produto | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResultado(null);

    const response = await converterProduto({
      skuEmbalado,
      skuAgranel,
      deposito,
      quantidade: 1,
    });

    if (response.success)
      setResultado(`Conversão realizada: ${response.mensagem}`);
    else setResultado(`Erro: ${response.error}`);

    setLoading(false);
  };

  const handleBlurEmbalado = async () => {
    if (skuEmbalado) {
      const response = await buscarProduto(skuEmbalado);
      if (response.success) setProdutoEmbaladoInfo(response.produtos[0]);
      else setProdutoEmbaladoInfo(null);
    }
  };

  const handleBlurAgranel = async () => {
    if (skuAgranel) {
      const response = await buscarProduto(skuAgranel);
      if (response.success) setProdutoAgranelInfo(response.produtos[0]);
      else setProdutoAgranelInfo(null);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 font-sans text-gray-800">
      <header className="bg-[#8CC63F] text-white py-2 shadow-md">
        <div className="container mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/images/lojamenor.png"
              alt="Lord Pets"
              width={100}
              height={40}
              priority
              className="h-auto w-auto"
            />
            <h1 className="text-xl font-bold">Conversor de Produtos</h1>
          </div>
          <p className="text-xs text-white/90 hidden sm:block">
            Converta embalados em granel facilmente
          </p>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-10">
        <section className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto border border-[#8CC63F]/30">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-[#6E2E1F]">
            <FaExchangeAlt /> Realizar Conversão
          </h2>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Produto Embalado */}
            <div>
              <label
                htmlFor="sku_embalado"
                className="block text-gray-700 mb-1 flex items-center gap-1"
              >
                <FaBox className="text-[#6E2E1F]" /> Produto Embalado
              </label>
              <input
                id="sku_embalado"
                type="text"
                placeholder="Ex: 2004"
                value={skuEmbalado}
                onChange={(e) => setSkuEmbalado(e.target.value)}
                onBlur={handleBlurEmbalado}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#8CC63F]"
              />
              {produtoEmbaladoInfo && (
                <div className="mt-2 text-sm text-gray-600 bg-gray-100 p-2 rounded">
                  <p><strong>Nome:</strong> {produtoEmbaladoInfo.nome}</p>
                  <p><strong>Código:</strong> {produtoEmbaladoInfo.codigo}</p>
                  {produtoEmbaladoInfo.pesoLiquido && (
                    <p><strong>Peso líquido:</strong> {produtoEmbaladoInfo.pesoLiquido} kg</p>
                  )}
                </div>
              )}
            </div>

            {/* Produto a Granel */}
            <div>
              <label
                htmlFor="sku_agranel"
                className="block text-gray-700 mb-1 flex items-center gap-1"
              >
                <FaBox className="text-[#6E2E1F]" /> Produto a Granel
              </label>
              <input
                id="sku_agranel"
                type="text"
                placeholder="Ex: 203"
                value={skuAgranel}
                onChange={(e) => setSkuAgranel(e.target.value)}
                onBlur={handleBlurAgranel}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#8CC63F]"
              />
              {produtoAgranelInfo && (
                <div className="mt-2 text-sm text-gray-600 bg-gray-100 p-2 rounded">
                  <p><strong>Nome:</strong> {produtoAgranelInfo.nome}</p>
                  <p><strong>Código:</strong> {produtoAgranelInfo.codigo}</p>
                  {produtoAgranelInfo.pesoLiquido && (
                    <p><strong>Peso líquido:</strong> {produtoAgranelInfo.pesoLiquido} kg</p>
                  )}
                </div>
              )}
            </div>

            {/* Depósito */}
            <div>
              <label htmlFor="deposito" className="block text-gray-700 mb-1">
                Depósito
              </label>
              <select
                id="deposito"
                value={deposito}
                onChange={(e) => setDeposito(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#8CC63F]"
              >
                <option value="Matriz">Matriz</option>
                <option value="Céu Azul">Céu Azul</option>
                <option value="Rio Branco">Rio Branco</option>
                <option value="São Benedito">São Benedito</option>
              </select>
            </div>

            {/* Botão */}
            <button
              type="submit"
              className="w-full bg-[#6E2E1F] text-white py-2 rounded-lg font-semibold hover:bg-[#541F16] transition"
              disabled={loading}
            >
              {loading ? "Convertendo..." : "Converter Produto"}
            </button>
          </form>

          {resultado && (
            <div className="mt-4 p-3 bg-[#f3fce8] rounded-md text-center flex items-center justify-center gap-2 text-[#6E2E1F]">
              <FaCheckCircle /> {resultado}
            </div>
          )}
        </section>
      </main>

      <footer className="bg-[#6E2E1F] text-white py-4 text-center">
        Desenvolvido para integração com Bling API |{" "}
        <span className="font-bold">Lord Pets</span>
      </footer>
    </div>
  );
};

export default Agranel;
