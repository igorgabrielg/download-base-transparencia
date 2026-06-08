import React, { useState, useEffect } from "react";
import { 
  Play, 
  RotateCcw, 
  Check, 
  X, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Download,
  Sparkles,
  Award,
  BookOpen,
  Plus,
  Edit2,
  Trash2
} from "lucide-react";
import toast from "react-hot-toast";

interface PerguntaTeste {
  id: number;
  pergunta: string;
  gabarito: string;
  tipo?: string;
  resposta_ia?: string;
  status?: "pendente" | "processando" | "concluido" | "erro";
  validacao?: "aceitavel" | "sinais de problemas" | "incorreto" | "correto";
  desvio_percentual?: number | null;
}

export function TestesAcuracia() {
  const [perguntas, setPerguntas] = useState<PerguntaTeste[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [progresso, setProgresso] = useState(0);
  
  // Estados para Modal de CRUD
  const [modalOpen, setModalOpen] = useState(false);
  const [perguntaInput, setPerguntaInput] = useState("");
  const [gabaritoInput, setGabaritoInput] = useState("");
  const [tipoInput, setTipoInput] = useState("Quantitativa");
  const [editingId, setEditingId] = useState<number | null>(null);

  // Carrega as perguntas do banco de dados ao iniciar
  const fetchPerguntas = async () => {
    try {
      const res = await fetch("/api/ia/testes-acuracia/perguntas");
      if (!res.ok) throw new Error("Erro ao buscar perguntas.");
      const data = await res.json();
      // Inicializa o status local para pendente
      setPerguntas(data.map((p: any) => ({ ...p, status: "pendente" })));
    } catch (err) {
      console.error(err);
      toast.error("Erro ao carregar perguntas do SQLite.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerguntas();
  }, []);

  // Inicia o processamento em tempo real (Stream)
  const startTesting = async () => {
    if (perguntas.length === 0) {
      toast.error("Nenhuma pergunta cadastrada para testes.");
      return;
    }
    
    setRunning(true);
    setProgresso(0);
    
    // Reseta estados temporários locais para iniciar a execução
    setPerguntas(prev => prev.map((p, idx) => ({ 
      ...p, 
      status: idx === 0 ? "processando" : "pendente", 
      resposta_ia: undefined, 
      validacao: undefined 
    })));
    
    try {
      const response = await fetch("/api/ia/testes-acuracia/stream");
      if (!response.body) throw new Error("Sem corpo de resposta de stream.");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        
        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const data = JSON.parse(line);
            
            setPerguntas(prev => prev.map(p => {
              if (p.id === data.id) {
                return {
                  ...p,
                  resposta_ia: data.resposta_ia,
                  status: "concluido",
                  validacao: data.validacao_sugerida,
                  desvio_percentual: data.desvio_percentual
                };
              }
              return p;
            }));
            
            // Avança para a próxima pergunta pendente
            setPerguntas(prev => prev.map((p, idx, arr) => {
              const currentIdx = arr.findIndex(item => item.id === data.id);
              if (idx === currentIdx + 1 && p.status === "pendente") {
                return { ...p, status: "processando" };
              }
              return p;
            }));
            
            setProgresso(prev => Math.min(prev + 1, perguntas.length));
            
          } catch (e) {
            console.error("Erro ao processar linha do stream:", e);
          }
        }
      }
      
      toast.success("Suíte de testes executada com sucesso!");
      fetchPerguntas(); // Atualiza a lista final para sincronizar tudo do banco
    } catch (err) {
      console.error("Erro ao ler stream de acurácia:", err);
      toast.error("Ocorreu um erro durante a execução da stream.");
    } finally {
      setRunning(false);
    }
  };

  // Cadastra ou edita uma pergunta no SQLite
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!perguntaInput.trim() || !gabaritoInput.trim()) {
      toast.error("Preencha todos os campos.");
      return;
    }

    try {
      if (editingId) {
        // Modo Edição
        const res = await fetch(`/api/ia/testes-acuracia/pergunta/${editingId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pergunta: perguntaInput, gabarito: gabaritoInput, tipo: tipoInput })
        });
        if (!res.ok) throw new Error("Falha ao editar.");
        toast.success("Pergunta atualizada!");
      } else {
        // Modo Cadastro
        const res = await fetch("/api/ia/testes-acuracia/pergunta", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pergunta: perguntaInput, gabarito: gabaritoInput, tipo: tipoInput })
        });
        if (!res.ok) throw new Error("Falha ao cadastrar.");
        toast.success("Pergunta cadastrada com sucesso!");
      }
      
      setModalOpen(false);
      setPerguntaInput("");
      setGabaritoInput("");
      setTipoInput("Quantitativa");
      setEditingId(null);
      fetchPerguntas();
    } catch (err) {
      console.error(err);
      toast.error("Erro ao salvar dados.");
    }
  };

  // Exclui uma pergunta
  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza que deseja excluir esta pergunta do teste?")) return;
    try {
      const res = await fetch(`/api/ia/testes-acuracia/pergunta/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Falha ao deletar.");
      toast.success("Pergunta excluída.");
      fetchPerguntas();
    } catch (err) {
      console.error(err);
      toast.error("Erro ao excluir pergunta.");
    }
  };

  // Executa um teste individual
  const runSingleTest = async (id: number) => {
    if (running) return;
    
    // Atualiza o status local da pergunta específica para processando
    setPerguntas(prev => prev.map(p => p.id === id ? { ...p, status: "processando", resposta_ia: undefined, validacao: undefined } : p));
    
    try {
      const res = await fetch(`/api/ia/testes-acuracia/pergunta/${id}/run`, {
        method: "POST"
      });
      if (!res.ok) throw new Error("Erro ao executar teste individual.");
      const data = await res.json();
      
      // Atualiza o estado com a resposta da IA e validação calculada pelo backend
      setPerguntas(prev => prev.map(p => p.id === id ? {
        ...p,
        resposta_ia: data.resposta_ia,
        status: "concluido",
        validacao: data.validacao,
        desvio_percentual: data.desvio_percentual
      } : p));
      
      toast.success("Teste individual concluído!");
    } catch (err) {
      console.error(err);
      toast.error("Erro ao executar teste individual.");
      setPerguntas(prev => prev.map(p => p.id === id ? { ...p, status: "erro" } : p));
    }
  };

  // Salva a validação manual (Correto/Incorreto) direto no banco SQLite
  const handleValidacao = async (id: number, status: "aceitavel" | "incorreto" | "sinais de problemas" | "correto") => {
    try {
      // Atualiza local instantaneamente para feedback visual rápido
      setPerguntas(prev => prev.map(p => p.id === id ? { ...p, validacao: status } : p));
      
      const res = await fetch(`/api/ia/testes-acuracia/pergunta/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ validacao: status })
      });
      if (!res.ok) throw new Error("Erro ao salvar validação.");
    } catch (err) {
      console.error(err);
      toast.error("Não foi possível salvar o voto no banco.");
    }
  };

  // Abre modal no modo de edição
  const openEditModal = (p: PerguntaTeste) => {
    setEditingId(p.id);
    setPerguntaInput(p.pergunta);
    setGabaritoInput(p.gabarito);
    setTipoInput(p.tipo || "Quantitativa");
    setModalOpen(true);
  };

  // Cálculos de estatísticas dinâmicos
  const totalPerguntas = perguntas.length;
  const totalRespondidas = perguntas.filter(p => p.resposta_ia).length;
  const corretasCount = perguntas.filter(p => p.resposta_ia && (p.validacao === "correto" || p.validacao === "aceitavel")).length;
  const incorretasCount = perguntas.filter(p => p.resposta_ia && p.validacao === "incorreto").length;
  const alertaCount = perguntas.filter(p => p.resposta_ia && p.validacao === "sinais de problemas").length;
  const acuraciaPercent = totalRespondidas > 0 ? ((corretasCount / totalRespondidas) * 100).toFixed(1) : "0.0";
  
  // Rejeições corretas para perguntas que esperavam erro de fato (tipo Segurança)
  const perguntasRejeicao = perguntas.filter(p => p.tipo === "Segurança");
  const totalRejeicoes = perguntasRejeicao.filter(p => p.resposta_ia).length;
  const rejeicoesCorretas = perguntasRejeicao.filter(p => p.resposta_ia && (p.validacao === "correto" || p.validacao === "aceitavel")).length;
  const rejeicaoPercent = totalRejeicoes > 0 ? ((rejeicoesCorretas / totalRejeicoes) * 100).toFixed(1) : "0.0";

  // Exportar relatório MD
  const exportReport = () => {
    let md = "# Relatório de Acurácia e Teste Sistemático do RAG\n\n";
    md += `Este relatório apresenta o teste de **${totalPerguntas} consultas** submetidas ao assistente virtual de auditoria, confrontando as respostas geradas com o gabarito real dos dados consolidados.\n\n`;
    md += `## Métricas de Avaliação Finais\n`;
    md += `- **Total de Perguntas submetidas:** ${totalPerguntas}\n`;
    md += `- **Perguntas Respondidas Corretamente (Acurácia):** ${corretasCount} / ${totalRespondidas} (${acuraciaPercent}%)\n`;
    md += `- **Perguntas com Rejeição Correta (Anti-alucinação):** ${rejeicoesCorretas} / ${totalRejeicoes} (${rejeicaoPercent}%)\n\n`;
    
    md += "## Tabela de Avaliação Sistemática\n\n";
    md += "| ID | Pergunta | Resposta Esperada (Gabarito) | Resposta Gerada pela IA | Desvio (%) | Status da Validação |\n";
    md += "|:---|:---|:---|:---|:---|:---|\n";
    
    perguntas.forEach(p => {
      const q = p.pergunta.replace("\n", " ");
      const g = p.gabarito.replace("\n", " ");
      const r = (p.resposta_ia || "Pendente").replace(/\n/g, " ");
      const desv = p.desvio_percentual !== undefined && p.desvio_percentual !== null
        ? `${p.desvio_percentual.toFixed(4)}%`
        : "N/A";
      const status = p.validacao === "aceitavel" || p.validacao === "correto"
        ? "Aceitável"
        : p.validacao === "sinais de problemas"
          ? "Sinais de Problemas"
          : p.validacao === "incorreto"
            ? "Incorreto"
            : "Pendente";
      md += `| ${p.id} | ${q} | ${g} | ${r} | ${desv} | ${status} |\n`;
    });

    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "relatorio_testes_acuracia_interface.md";
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="h-[400px] flex flex-col items-center justify-center gap-3">
        <Loader2 className="animate-spin text-[var(--theme-accent)]" size={32} />
        <span className="text-xs text-[var(--theme-text-secondary)] font-medium">Carregando testes do SQLite...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1200px] mx-auto p-4 sm:p-6 animate-fade-in text-[var(--theme-text)]">
      {/* Cabeçalho */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] shadow-sm">
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Award className="text-[var(--theme-accent)]" size={22} /> Avaliação Sistemática de Acurácia (TCC)
          </h2>
          <p className="text-xs text-[var(--theme-text-secondary)]">
            Cadastre perguntas, edite e valide os resultados do chat RAG salvando as informações diretamente no banco SQLite local.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => {
              setEditingId(null);
              setPerguntaInput("");
              setGabaritoInput("");
              setTipoInput("Quantitativa");
              setModalOpen(true);
            }}
            disabled={running}
            className="px-3.5 py-2 border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/60 hover:bg-[var(--theme-surface-2)] rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
          >
            <Plus size={14} /> Cadastrar Pergunta
          </button>

          <button
            onClick={startTesting}
            disabled={running}
            className="px-4 py-2 bg-[var(--theme-accent)] hover:bg-[var(--theme-accent)]/90 text-white rounded-lg text-xs font-semibold flex items-center gap-2 disabled:opacity-50 transition-colors cursor-pointer"
          >
            {running ? (
              <>
                <Loader2 size={15} className="animate-spin" /> Testando ({progresso}/{totalPerguntas})
              </>
            ) : (
              <>
                <Play size={15} /> Iniciar Teste Geral
              </>
            )}
          </button>
          
          <button
            onClick={exportReport}
            disabled={running || totalRespondidas === 0}
            className="px-4 py-2 border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/60 hover:bg-[var(--theme-surface-2)] rounded-lg text-xs font-semibold flex items-center gap-2 disabled:opacity-40 transition-colors cursor-pointer"
          >
            <Download size={15} /> Exportar MD
          </button>
        </div>
      </div>

      {/* Grid de Estatísticas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Respondidas */}
        <div className="p-5 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] shadow-sm flex flex-col justify-between h-[110px]">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--theme-text-secondary)] flex items-center gap-1.5">
            <BookOpen size={12} className="text-blue-500" /> Total Avaliado
          </span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold">{totalRespondidas}</span>
            <span className="text-xs text-[var(--theme-text-secondary)]">/ {totalPerguntas}</span>
          </div>
          <div className="w-full bg-[var(--theme-border)] h-1.5 rounded-full mt-3 overflow-hidden">
            <div 
              className="bg-blue-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${totalPerguntas > 0 ? (totalRespondidas / totalPerguntas) * 100 : 0}%` }}
            />
          </div>
        </div>

        {/* Card 2: Acurácia */}
        <div className="p-5 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] shadow-sm flex flex-col justify-between h-[110px]">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--theme-text-secondary)] flex items-center gap-1.5">
            <Award size={12} className="text-[var(--theme-success)]" /> Acurácia Global
          </span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-[var(--theme-success)]">{acuraciaPercent}%</span>
          </div>
          <span className="text-[10px] text-[var(--theme-text-secondary)] font-medium mt-3">
            {corretasCount} respostas validadas como corretas.
          </span>
        </div>

        {/* Card 3: Anti-alucinação */}
        <div className="p-5 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] shadow-sm flex flex-col justify-between h-[110px]">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--theme-text-secondary)] flex items-center gap-1.5">
            <Sparkles size={12} className="text-[var(--theme-warning)]" /> Rejeições Corretas
          </span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-[var(--theme-warning)]">{rejeicaoPercent}%</span>
          </div>
          <span className="text-[10px] text-[var(--theme-text-secondary)] font-medium mt-3">
            {rejeicoesCorretas} rejeições de {totalRejeicoes} solicitadas.
          </span>
        </div>

        {/* Card 4: Incorretas */}
        <div className="p-5 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] shadow-sm flex flex-col justify-between h-[110px]">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--theme-text-secondary)] flex items-center gap-1.5">
            <AlertCircle size={12} className="text-[var(--theme-danger)]" /> Respostas Incorretas
          </span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-[var(--theme-danger)]">{incorretasCount}</span>
            <span className="text-xs text-[var(--theme-text-secondary)]">consultas</span>
          </div>
          <span className="text-[10px] text-[var(--theme-text-secondary)] font-medium mt-3">
            Total de respostas com erros/desvios.
          </span>
        </div>
      </div>

      {/* Tabela de Perguntas */}
      <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-[var(--theme-border)] bg-[var(--theme-surface-2)]/30 text-[var(--theme-text-secondary)] font-semibold">
                <th className="p-4 w-12 text-center">ID</th>
                <th className="p-4 w-[25%]">Pergunta de Teste</th>
                <th className="p-4 w-[20%]">Gabarito Esperado</th>
                <th className="p-4 w-[35%]">Resposta Gerada pela IA</th>
                <th className="p-4 w-28 text-center">Ações</th>
                <th className="p-4 w-28 text-center">Validação (TCC)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--theme-border)]">
              {perguntas.map((p, index) => {
                const isProcessing = p.status === "processando";
                const isConcluido = p.status === "concluido" || p.resposta_ia;
                const isDescontinuado = false;
                
                return (
                  <tr 
                    key={p.id}
                    className={`transition-colors hover:bg-[var(--theme-surface-2)]/25 ${
                      isProcessing ? "bg-[var(--theme-accent)]/5" : ""
                    }`}
                  >
                    <td className="p-4 font-bold text-center border-r border-[var(--theme-border)] text-[var(--theme-text-secondary)] bg-[var(--theme-surface-2)]/10">
                      {index + 1}
                    </td>
                    <td className="p-4 font-semibold leading-relaxed">
                      <div>{p.pergunta}</div>
                      <div className="mt-1.5 flex gap-1">
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border transition-colors ${
                          p.tipo === "Quantitativa"
                            ? "bg-blue-500/10 text-blue-500 border-blue-500/20"
                            : p.tipo === "Qualitativa baseada em dados"
                              ? "bg-purple-500/10 text-purple-500 border-purple-500/20"
                              : p.tipo === "Qualitativa interpretativa"
                                ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                                : "bg-red-500/10 text-red-500 border-red-500/20"
                        }`}>
                          {p.tipo || "Quantitativa"}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-[var(--theme-text-secondary)] font-mono text-[10px] leading-relaxed">
                      {isDescontinuado ? "Não faz parte do escopo da pesquisa." : p.gabarito}
                    </td>
                    <td className="p-4 leading-relaxed whitespace-pre-wrap">
                      {isDescontinuado ? (
                        <span className="text-[var(--theme-text-secondary)] italic text-[11px]">Não faz parte do escopo da pesquisa.</span>
                      ) : (
                        <>
                          {isProcessing && (
                            <div className="flex items-center gap-2 text-[var(--theme-accent)] italic font-medium animate-pulse text-[11px]">
                              <Loader2 size={14} className="animate-spin text-[var(--theme-accent)]" />
                              Consultando RAG...
                            </div>
                          )}
                          
                          {p.status === "pendente" && !p.resposta_ia && (
                            <span className="text-[var(--theme-text-secondary)]/30 italic text-[11px]">Aguardando teste...</span>
                          )}

                          {p.status === "erro" && (
                            <span className="text-[var(--theme-danger)] font-medium text-[11px] flex items-center gap-1.5">
                              <XCircle size={14} /> Erro na conexão
                            </span>
                          )}
                          
                          {p.resposta_ia && (
                            <div className="space-y-2">
                              <div className="text-[11px] font-normal leading-relaxed text-[var(--theme-text)]">
                                {p.resposta_ia}
                              </div>
                              
                              {p.desvio_percentual !== undefined && p.desvio_percentual !== null && (
                                <div className="flex items-center gap-1.5 flex-wrap">
                                  <span className="text-[9px] text-[var(--theme-text-secondary)] font-semibold uppercase tracking-wide">Desvio Relativo:</span>
                                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border transition-colors ${
                                    p.desvio_percentual === 0
                                      ? "bg-green-500/10 text-green-500 border-green-500/20"
                                      : p.desvio_percentual < 0.5
                                        ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                                        : p.desvio_percentual <= 5.0
                                          ? "bg-amber-500/10 text-amber-500 border-amber-500/20"
                                          : "bg-red-500/10 text-red-500 border-red-500/20"
                                  }`}>
                                    {p.desvio_percentual === 0 ? "0.0000% (Exato)" : `${p.desvio_percentual.toFixed(4)}%`}
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      )}
                    </td>
                    {/* Ações (Executar/Editar/Excluir) */}
                    <td className="p-4 text-center border-l border-[var(--theme-border)]">
                      {isDescontinuado ? (
                        <span className="text-[10px] text-[var(--theme-text-secondary)] italic">Ignorado</span>
                      ) : (
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => runSingleTest(p.id)}
                            disabled={running || p.status === "processando"}
                            title="Executar Teste Individual"
                            className="p-1.5 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/40 hover:bg-[var(--theme-success)]/10 hover:border-[var(--theme-success)]/30 hover:text-[var(--theme-success)] transition-all cursor-pointer disabled:opacity-40"
                          >
                            {p.status === "processando" ? (
                              <Loader2 size={13} className="animate-spin" />
                            ) : (
                              <Play size={13} />
                            )}
                          </button>

                          <button
                            onClick={() => openEditModal(p)}
                            disabled={running || p.status === "processando"}
                            title="Editar Pergunta"
                            className="p-1.5 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/40 hover:bg-[var(--theme-accent)]/10 hover:border-[var(--theme-accent)]/30 hover:text-[var(--theme-accent)] transition-all cursor-pointer disabled:opacity-40"
                          >
                            <Edit2 size={13} />
                          </button>
                          
                          <button
                            onClick={() => handleDelete(p.id)}
                            disabled={running || p.status === "processando"}
                            title="Excluir Pergunta"
                            className="p-1.5 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/40 hover:bg-[var(--theme-danger)]/10 hover:border-[var(--theme-danger)]/30 hover:text-[var(--theme-danger)] transition-all cursor-pointer disabled:opacity-40"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      )}
                    </td>
                    {/* Validação (Correto/Incorreto) */}
                    <td className="p-4 border-l border-[var(--theme-border)]">
                      {isDescontinuado ? (
                        <div className="flex justify-center">
                          <span className="text-[10px] font-bold text-[var(--theme-text-secondary)] bg-[var(--theme-text-secondary)]/10 px-2 py-0.5 rounded-full border border-[var(--theme-text-secondary)]/20">
                            Descontinuado
                          </span>
                        </div>
                      ) : (
                        p.resposta_ia && (
                          <div className="flex flex-col gap-1 items-center justify-center">
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleValidacao(p.id, p.validacao === "aceitavel" ? "correto" : "aceitavel")}
                                disabled={running}
                                title="Marcar como Aceitável"
                                className={`p-1.5 rounded-lg border transition-all cursor-pointer ${
                                  p.validacao === "aceitavel" || p.validacao === "correto"
                                    ? "bg-[var(--theme-success)]/10 border-[var(--theme-success)] text-[var(--theme-success)] scale-110 shadow-sm"
                                    : "border-[var(--theme-border)] bg-[var(--theme-surface-2)]/40 text-[var(--theme-text-secondary)] hover:border-[var(--theme-success)]/50 hover:text-[var(--theme-success)]"
                                }`}
                              >
                                <Check size={14} />
                              </button>
                              
                              <button
                                onClick={() => handleValidacao(p.id, p.validacao === "incorreto" ? "correto" : "incorreto")}
                                disabled={running}
                                title="Marcar como Incorreta"
                                className={`p-1.5 rounded-lg border transition-all cursor-pointer ${
                                  p.validacao === "incorreto"
                                    ? "bg-[var(--theme-danger)]/10 border-[var(--theme-danger)] text-[var(--theme-danger)] scale-110 shadow-sm"
                                    : "border-[var(--theme-border)] bg-[var(--theme-surface-2)]/40 text-[var(--theme-text-secondary)] hover:border-[var(--theme-danger)]/50 hover:text-[var(--theme-danger)]"
                                }`}
                              >
                                <X size={14} />
                              </button>
                            </div>
                            
                            {(p.validacao === "aceitavel" || p.validacao === "correto") && (
                              <span className="text-[9px] font-bold text-[var(--theme-success)] flex items-center gap-0.5 mt-0.5">
                                <CheckCircle2 size={10} /> Aceitável
                              </span>
                            )}

                            {p.validacao === "sinais de problemas" && (
                              <span className="text-[9px] font-bold text-[var(--theme-warning)] flex items-center gap-0.5 mt-0.5">
                                <AlertCircle size={10} /> Sinais de Problemas
                              </span>
                            )}
                            
                            {p.validacao === "incorreto" && (
                              <span className="text-[9px] font-bold text-[var(--theme-danger)] flex items-center gap-0.5 mt-0.5">
                                <XCircle size={10} /> Incorreto
                              </span>
                            )}
                          </div>
                        )
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de Criação / Edição */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-[500px] rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-surface-1)] p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-[var(--theme-border)] pb-3">
              <h3 className="text-sm font-bold tracking-wide uppercase flex items-center gap-1.5">
                <BookOpen size={16} className="text-[var(--theme-accent)]" /> 
                {editingId ? "Editar Pergunta de Teste" : "Cadastrar Pergunta de Teste"}
              </h3>
              <button 
                onClick={() => setModalOpen(false)}
                className="text-[var(--theme-text-secondary)] hover:text-[var(--theme-text)] cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs font-semibold">
              <div className="space-y-1.5">
                <label className="text-[10px] text-[var(--theme-text-secondary)] uppercase tracking-wider">Pergunta do Teste</label>
                <textarea
                  required
                  rows={3}
                  value={perguntaInput}
                  onChange={(e) => setPerguntaInput(e.target.value)}
                  placeholder="Ex: Qual foi a despesa liquidada da Função Previdência Social em 2025?"
                  className="w-full px-3 py-2 border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/30 rounded-lg text-xs font-medium text-[var(--theme-text)] focus:border-[var(--theme-accent)] outline-none resize-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] text-[var(--theme-text-secondary)] uppercase tracking-wider">Tipo Técnico da Pergunta</label>
                <select
                  value={tipoInput}
                  onChange={(e) => setTipoInput(e.target.value)}
                  className="w-full px-3 py-2 border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/30 rounded-lg text-xs font-semibold text-[var(--theme-text)] focus:border-[var(--theme-accent)] outline-none cursor-pointer"
                >
                  <option value="Quantitativa">Quantitativa</option>
                  <option value="Qualitativa baseada em dados">Qualitativa baseada em dados</option>
                  <option value="Qualitativa interpretativa">Qualitativa interpretativa</option>
                  <option value="Segurança">Segurança</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] text-[var(--theme-text-secondary)] uppercase tracking-wider">Gabarito Esperado (Valor de Referência)</label>
                <textarea
                  required
                  rows={2}
                  value={gabaritoInput}
                  onChange={(e) => setGabaritoInput(e.target.value)}
                  placeholder="Ex: R$ 1.098.483.168.531,61 (22,33% da despesa total)."
                  className="w-full px-3 py-2 border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/30 rounded-lg text-xs font-medium text-[var(--theme-text)] focus:border-[var(--theme-accent)] outline-none resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 border border-[var(--theme-border)] bg-[var(--theme-surface-2)]/60 text-[var(--theme-text)] rounded-lg text-xs font-bold transition-all cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[var(--theme-accent)] hover:bg-[var(--theme-accent)]/90 text-white rounded-lg text-xs font-bold transition-all cursor-pointer"
                >
                  Salvar Pergunta
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
