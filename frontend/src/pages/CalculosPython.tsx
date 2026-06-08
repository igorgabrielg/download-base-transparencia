import { useState, useEffect } from "react";
import { Calculator, Loader2, RefreshCw, HelpCircle, CheckCircle, AlertTriangle } from "lucide-react";
import { iaApi } from "@/api/endpoints";
import toast from "react-hot-toast";

interface CalculoItem {
  id: number;
  pergunta: string;
  calculo_python: string;
}

// Lista fixa de gabaritos para exibição lado a lado
const GABARITOS: Record<number, string> = {
  1: "A participação foi de 4,39% (com R$ 215,84 bilhões executados).",
  2: "R$ 4.918.934.850.159,02 (aproximadamente R$ 4,92 trilhões).",
  3: "R$ 5.614.085.003.109,29 (aproximadamente R$ 5,61 trilhões).",
  4: "22,33% da despesa total (com R$ 1,09 trilhão executados).",
  5: "4,61% da despesa total.",
  6: "R$ 4.506.144.942.426,41.",
  7: "Coordenação-Geral de Controle da Dívida Pública (CODIV) - UG 170600.",
  8: "R$ 2.127.695.030.497,72 (43,26% da despesa total da União).",
  9: "Esta pergunta não faz parte do escopo da pesquisa e nem pertence a calculos",
  10: "Rigidez orçamentária com frustração de receitas, serviço da dívida pública elevado (CODIV) e inconsistência cadastral no SIAFI.",
  11: "Frustração crítica de -98,56% (ou -R$ 42,25 bilhões frente ao orçado).",
  12: "R$ 115.998.757.609,17.",
  13: "111,77% (com receita realizada de R$ 51,61 bilhões frente a R$ 46,18 bilhões previstos).",
  14: "O Ministério do Trabalho conseguiu se manter de forma sustentável no período. Despesas totais: R$ 115.998.757.609,17. Receitas próprias: R$ 131.350.890.946,54. Diferença: R$ 15.352.133.337,37.",
  15: "2,56% do orçamento total (aproximadamente R$ 125,9 bilhões).",
  16: "Devido a uma frustração de 98,56% em suas receitas previstas, enquanto suas despesas com programas sociais continuaram rígidas.",
  17: "76,69% do orçamento global da União.",
  18: "Aproximadamente 0,001% cada, orçamentos marginais pela natureza transversal.",
  19: "Não deve constar na base ou indicar erro de processamento.",
  20: "Não deve constar na base ou indicar erro de processamento."
};

export function CalculosPython() {
  const [itens, setItens] = useState<CalculoItem[]>([]);
  const [gabaritosDinamicos, setGabaritosDinamicos] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [reprocessing, setReprocessing] = useState(false);

  async function carregarCalculos() {
    setLoading(true);
    try {
      const data = await iaApi.calculosPython();
      setItens(data);
      
      const res = await fetch("/api/ia/testes-acuracia/perguntas");
      if (res.ok) {
        const perguntas = await res.json();
        const mapa: Record<number, string> = {};
        perguntas.forEach((p: any) => {
          mapa[p.id] = p.gabarito;
        });
        setGabaritosDinamicos(mapa);
      }
    } catch (error: any) {
      console.error(error);
      const detail = error.response?.data?.detail || error.message || "Erro desconhecido.";
      toast.error(`Erro ao carregar cálculos: ${detail}`);
    } finally {
      setLoading(false);
    }
  }

  async function reprocessarEImportarTodos() {
    setReprocessing(true);
    try {
      const data = await iaApi.processarCalculosPython();
      setItens(data);
      
      const res = await fetch("/api/ia/testes-acuracia/perguntas");
      if (res.ok) {
        const perguntas = await res.json();
        const mapa: Record<number, string> = {};
        perguntas.forEach((p: any) => {
          mapa[p.id] = p.gabarito;
        });
        setGabaritosDinamicos(mapa);
      }
      
      toast.success("Todos os dados de 2025 foram reprocessados e gravados no SQLite!");
    } catch (error: any) {
      console.error(error);
      const detail = error.response?.data?.detail || error.message || "Erro desconhecido.";
      toast.error(`Erro ao reprocessar: ${detail}`, { duration: 6000 });
    } finally {
      setReprocessing(false);
    }
  }

  useEffect(() => {
    carregarCalculos();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3">
            <Calculator className="text-[var(--theme-accent)]" size={28} />
            Cálculos e Auditoria em Python
          </h2>
          <p className="text-body text-[var(--theme-text-secondary)] mt-1">
            Resultados calculados programmaticamente em tempo real diretamente do banco de dados SQLite para validar os gabaritos oficiais.
          </p>
        </div>
        <div className="flex gap-2 self-start md:self-center">
          <button
            onClick={reprocessarEImportarTodos}
            disabled={loading || reprocessing}
            className="btn btn-primary flex items-center gap-2"
          >
            {reprocessing ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <RefreshCw size={16} />
            )}
            Processar todos novamente
          </button>
          
          <button
            onClick={carregarCalculos}
            disabled={loading || reprocessing}
            className="btn btn-secondary flex items-center gap-2"
          >
            {loading && !reprocessing ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Calculator size={16} />
            )}
            Recalcular
          </button>
        </div>
      </div>

      {loading || reprocessing ? (
        <div className="flex flex-col items-center justify-center p-12 bg-[var(--theme-card)] rounded-xl border border-[var(--theme-border)]">
          <Loader2 size={36} className="animate-spin text-[var(--theme-accent)] mb-4" />
          <span className="text-sm text-[var(--theme-text-secondary)]">
            {reprocessing
              ? "Importando arquivos CSV de 2025 para o SQLite e recalculando... (Isso pode levar alguns instantes)"
              : "Calculando valores orçamentários em Python..."}
          </span>
        </div>
      ) : itens.length === 0 ? (
        <div className="p-8 bg-[var(--theme-card)] rounded-xl border border-[var(--theme-border)] text-center space-y-3">
          <AlertTriangle className="mx-auto text-[var(--theme-warning)]" size={40} />
          <h3 className="text-h4 text-[var(--theme-text)]">Nenhum cálculo pôde ser realizado</h3>
          <p className="text-sm text-[var(--theme-text-secondary)] max-w-md mx-auto">
            Certifique-se de ter concluído o download e o enriquecimento de dados das despesas e receitas no ano de 2025 antes de realizar a auditoria dos cálculos.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {itens.map((item) => {
            const gabarito = gabaritosDinamicos[item.id] || GABARITOS[item.id] || "Não cadastrado";
            const isForaDoEscopo = gabarito.toLowerCase().includes("não deve constar na base") || 
                                   item.calculo_python.toLowerCase().includes("não faz parte do escopo") ||
                                   item.calculo_python.toLowerCase().includes("não pertence a calculos");
            // Normalizamos para ver se o cálculo bate minimamente com a resposta
            const batimentoVisual = item.calculo_python.toLowerCase().replace(/[^a-z0-9]/g, "") === gabarito.toLowerCase().replace(/[^a-z0-9]/g, "");

            return (
              <div
                key={item.id}
                className="bg-[var(--theme-card)] border border-[var(--theme-border)] rounded-xl p-5 hover:border-[var(--theme-text-secondary)]/30 transition-all space-y-4 shadow-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center justify-center w-7 h-7 rounded-full bg-[var(--theme-accent)]/10 text-[var(--theme-accent)] font-bold text-xs">
                      {item.id}
                    </span>
                    <h3 className="text-sm font-semibold text-[var(--theme-text)]">
                      {item.pergunta}
                    </h3>
                  </div>
                  {isForaDoEscopo ? null : batimentoVisual ? (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-[var(--theme-success)] bg-[var(--theme-success)]/10 px-2 py-0.5 rounded-full">
                      <CheckCircle size={12} /> Bate 100%
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-[var(--theme-warning)] bg-[var(--theme-warning)]/10 px-2 py-0.5 rounded-full">
                      <HelpCircle size={12} /> Validar Manual
                    </span>
                  )}
                </div>

                {isForaDoEscopo ? (
                  <div className="p-4 bg-[var(--theme-surface-2)]/30 rounded-lg text-xs text-[var(--theme-text-secondary)] border border-[var(--theme-border)] leading-relaxed min-h-[50px] flex items-center justify-center font-semibold w-full">
                    Esta pergunta não faz parte do escopo da pesquisa e nem pertence a calculos
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-[var(--theme-border)]">
                    <div className="space-y-1">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--theme-text-secondary)]">
                        Gabarito Oficial (Esperado)
                      </span>
                      <div className="p-3 bg-[var(--theme-bg)]/40 rounded-lg text-xs font-mono text-[var(--theme-text)] border border-[var(--theme-border)]/50 leading-relaxed min-h-[50px] flex items-center">
                        {gabarito}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--theme-accent)]">
                        Cálculo Dinâmico Python (Obtido)
                      </span>
                      <div className="p-3 bg-[var(--theme-accent)]/5 rounded-lg text-xs font-mono text-[var(--theme-accent)] border border-[var(--theme-accent)]/20 leading-relaxed min-h-[50px] flex items-center">
                        {item.calculo_python}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
