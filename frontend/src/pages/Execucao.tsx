import { useState, useRef, useEffect } from "react";
import { Play, Pause, Square, RefreshCw, Loader2, Settings, ExternalLink, FolderOutput, Cpu } from "lucide-react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

import { useDownload } from "@/hooks/useDownload";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useConfig, useAnalyzeIA, useSynthesizeIA, useIndexIA, usePipelineCompletoIA } from "@/hooks/useConfig";
import { Badge } from "@/components/ui/Badge";
import { Gauge } from "@/components/ui/Gauge";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { LogEntry, ExecutionStatus } from "@/types";

const statusConfig: Record<ExecutionStatus, { variant: "success" | "warning" | "error" | "info"; label: string }> = {
  parado: { variant: "info", label: "Parado" },
  executando: { variant: "success", label: "Executando" },
  pausado: { variant: "warning", label: "Pausado" },
  erro: { variant: "error", label: "Erro" },
  concluido: { variant: "success", label: "Concluido" },
};

interface ConsoleLog {
  timestamp: string;
  level: "info" | "warning" | "error" | "success";
  message: string;
}

export function Execucao() {
  const { start, pause, resume, stop } = useDownload();
  const { status, connected } = useWebSocket();
  const { data: config } = useConfig();
  const analyzeIA = useAnalyzeIA();
  const synthesizeIA = useSynthesizeIA();
  const indexIA = useIndexIA();
  const pipelineCompletoIA = usePipelineCompletoIA();
  const [showStopDialog, setShowStopDialog] = useState(false);
  const [consoleLogs, setConsoleLogs] = useState<ConsoleLog[]>(() => {
    try {
      const saved = localStorage.getItem("execucao_console_logs");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      localStorage.setItem("execucao_console_logs", JSON.stringify(consoleLogs));
    } catch (e) {
      console.error("Erro ao salvar logs no localStorage", e);
    }
  }, [consoleLogs]);

  const isRunning = status?.status === "executando";
  const isPaused = status?.status === "pausado";
  const isStopped = !status || status.status === "parado" || status.status === "concluido";

  useEffect(() => {
    if (status) {
      const now = new Date().toLocaleTimeString("pt-BR");
      setConsoleLogs((prev) => {
        let level: ConsoleLog["level"] = "info";
        let message = "";

        if (status.mensagem) {
          // Mensagem descritiva do backend
          const isSkip = status.mensagem.includes("pulando") || status.mensagem.includes("ja baixado");
          const isConcluido = status.status === "concluido";
          const isNenhum = status.mensagem.includes("Nenhum novo download");
          level = isConcluido ? "success" : isSkip ? "warning" : isNenhum ? "warning" : status.status === "erro" ? "error" : "info";
          message = status.mensagem;
        } else {
          level = status.status === "erro" ? "error" : status.status === "executando" ? "info" : "warning";
          message = `${status.endpoint_atual ?? "-"} ${status.ano_mes_atual ?? "-"} | Pg ${status.pagina_atual} | ${status.total_registros.toLocaleString()} registros | ${status.req_minuto} req/min`;
        }

        const newLog: ConsoleLog = { timestamp: now, level, message };
        const next = [...prev, newLog];
        return next.slice(-200);
      });
    }
  }, [status?.pagina_atual, status?.status, status?.req_minuto, status?.msg_seq]);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [consoleLogs]);

  function handleStart() {
    start.mutate(undefined, {
      onSuccess: () => {
        toast.success("Download iniciado.");
        setConsoleLogs((prev) => [...prev, { timestamp: new Date().toLocaleTimeString("pt-BR"), level: "success", message: "Download iniciado com sucesso." }]);
      },
      onError: () => toast.error("Nao foi possivel iniciar o download."),
    });
  }

  function handlePause() {
    pause.mutate(undefined, {
      onSuccess: () => toast("Download pausado.", { icon: "\u23F8\uFE0F" }),
      onError: () => toast.error("Nao foi possivel pausar o download."),
    });
  }

  function handleResume() {
    resume.mutate(undefined, {
      onSuccess: () => toast.success("Download retomado."),
      onError: () => toast.error("Nao foi possivel retomar o download."),
    });
  }

  function handleStop() {
    setShowStopDialog(true);
  }

  function confirmStop() {
    setShowStopDialog(false);
    stop.mutate(undefined, {
      onSuccess: () => toast("Download parado. O progresso foi salvo.", { icon: "\u23F9\uFE0F" }),
      onError: () => toast.error("Nao foi possivel parar o download."),
    });
  }

  function handleAnalyzeIA() {
    analyzeIA.mutate(undefined, {
      onSuccess: () => {
        toast.success("Analise cognitiva de IA iniciada em background.");
        setConsoleLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toLocaleTimeString("pt-BR"),
            level: "success",
            message: "Agentes de IA disparados com sucesso em background.",
          },
        ]);
      },
      onError: () => toast.error("Nao foi possivel iniciar a analise de IA. Verifique chaves de API."),
    });
  }

  function handleSynthesizeIA() {
    synthesizeIA.mutate(undefined, {
      onSuccess: () => {
        toast.success("Sintese e consolidacao de IA iniciada em segundo plano.");
        setConsoleLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toLocaleTimeString("pt-BR"),
            level: "success",
            message: "Auditor-Chefe acionado com sucesso para redacao final.",
          },
        ]);
      },
      onError: () => toast.error("Nao foi possivel iniciar a sintese de IA. Verifique chaves de API."),
    });
  }

  function handleIndexIA() {
    indexIA.mutate(undefined, {
      onSuccess: () => {
        toast.success("Indexacao vetorial de IA iniciada em segundo plano.");
        setConsoleLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toLocaleTimeString("pt-BR"),
            level: "success",
            message: "Pipeline de indexacao vetorial disparado com sucesso no ChromaDB.",
          },
        ]);
      },
      onError: () => toast.error("Nao foi possivel iniciar a indexacao de IA."),
    });
  }

  function handlePipelineCompletoIA() {
    pipelineCompletoIA.mutate(undefined, {
      onSuccess: () => {
        toast.success("Pipeline completo de IA iniciado em background.");
        setConsoleLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toLocaleTimeString("pt-BR"),
            level: "success",
            message: "Pipeline de IA completo disparado com sucesso (Etapas 1 a 4).",
          },
        ]);
      },
      onError: (err: any) => {
        const errMsg = err.response?.data?.detail || err.message || "Erro desconhecido";
        toast.error(`Nao foi possivel iniciar o pipeline: ${errMsg}`);
      },
    });
  }

  const executionStatus = status ? statusConfig[status.status] : null;
  const reqMax = status?.token_statuses?.[0]?.limite_aplicavel ?? 400;

  return (
    <div>
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <Play size={24} /> Painel de Execucao
      </h2>

      {/* Action bar */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="btn btn-primary"
            onClick={handleStart}
            disabled={!isStopped || start.isPending}
          >
            {start.isPending ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            Iniciar Download
          </button>
          <button
            className="btn btn-warning"
            onClick={handlePause}
            disabled={!isRunning || pause.isPending}
          >
            <Pause size={16} /> Pausar
          </button>
          <button
            className="btn btn-success"
            onClick={handleResume}
            disabled={!isPaused || resume.isPending}
          >
            <RefreshCw size={16} /> Retomar
          </button>
          <button
            className="btn btn-danger"
            onClick={handleStop}
            disabled={isStopped || stop.isPending}
          >
            <Square size={16} /> Parar Download
          </button>
          
          <button
            className="btn btn-warning flex items-center gap-2"
            onClick={handleAnalyzeIA}
            disabled={!isStopped || analyzeIA.isPending}
            style={{ backgroundColor: "var(--theme-warning)", color: "#000" }}
          >
            {analyzeIA.isPending ? <Loader2 size={16} className="animate-spin" /> : <Cpu size={16} />}
            Iniciar Analise Cognitiva (IA)
          </button>

          <button
            className="btn btn-primary flex items-center gap-2"
            onClick={handleSynthesizeIA}
            disabled={!isStopped || synthesizeIA.isPending}
            style={{ backgroundColor: "#8b5cf6", borderColor: "#8b5cf6", color: "#fff" }}
          >
            {synthesizeIA.isPending ? <Loader2 size={16} className="animate-spin" /> : <Cpu size={16} />}
            Consolidar Relatorio (IA)
          </button>

          <button
            className="btn flex items-center gap-2 text-white"
            onClick={handleIndexIA}
            disabled={!isStopped || indexIA.isPending}
            style={{ backgroundColor: "#10b981", borderColor: "#10b981" }}
          >
            {indexIA.isPending ? <Loader2 size={16} className="animate-spin" /> : <Cpu size={16} />}
            Indexar Relatorio (IA)
          </button>

          <button
            className="btn flex items-center gap-2 text-white font-semibold cursor-pointer animate-hover-button"
            onClick={handlePipelineCompletoIA}
            disabled={!isStopped || pipelineCompletoIA.isPending}
            style={{ background: "linear-gradient(135deg, #a855f7 0%, #6366f1 100%)", borderColor: "transparent" }}
          >
            {pipelineCompletoIA.isPending ? <Loader2 size={16} className="animate-spin" /> : <Cpu size={16} />}
            Executar Pipeline Completo (Etapas 1-4)
          </button>

          <div className="ml-auto flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${connected ? "bg-[var(--theme-success)]" : "bg-[var(--theme-error)]"}`} />
            <span className="text-caption text-[var(--theme-text-secondary)]">
              {connected ? "Conectado" : "Desconectado"}
            </span>
          </div>
        </div>
      </div>

      {/* Config summary */}
      {config && (
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-h4 text-[var(--theme-text)] flex items-center gap-2">
              <Settings size={18} /> Configuracao Atual
            </h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div>
              <span className="text-caption text-[var(--theme-text-secondary)]">Tokens</span>
              <p className="text-mono font-medium text-[var(--theme-text)]">
                {config.tokens_count} configurado{config.tokens_count !== 1 ? "s" : ""}
              </p>
              <Link to="/config/tokens" className="text-caption text-[var(--theme-accent)] hover:underline flex items-center gap-1 mt-1">
                Editar <ExternalLink size={10} />
              </Link>
            </div>
            <div>
              <span className="text-caption text-[var(--theme-text-secondary)]">Periodo</span>
              <p className="text-mono font-medium text-[var(--theme-text)]">
                {String(config.mes_inicio).padStart(2, "0")}/{config.ano_inicio} a {String(config.mes_fim).padStart(2, "0")}/{config.ano_fim}
              </p>
              <Link to="/config/periodo" className="text-caption text-[var(--theme-accent)] hover:underline flex items-center gap-1 mt-1">
                Editar <ExternalLink size={10} />
              </Link>
            </div>
            <div>
              <span className="text-caption text-[var(--theme-text-secondary)]">Endpoints</span>
              <p className="text-mono font-medium text-[var(--theme-text)]">
                {[config.baixar_despesas && "Despesas", config.baixar_receitas && "Receitas"].filter(Boolean).join(", ")}
              </p>
              <Link to="/config/endpoints" className="text-caption text-[var(--theme-accent)] hover:underline flex items-center gap-1 mt-1">
                Editar <ExternalLink size={10} />
              </Link>
            </div>
            <div>
              <span className="text-caption text-[var(--theme-text-secondary)]">Rate Limit</span>
              <p className="text-mono font-medium text-[var(--theme-text)]">
                {config.max_req_dia}/min (dia) | {config.max_req_madrugada}/min (noite)
              </p>
              <p className="text-mono text-sm text-[var(--theme-text-secondary)]">
                Velocidade: {config.velocidade_req_min} req/min (~{(60 / config.velocidade_req_min).toFixed(1)}s/req)
              </p>
              <Link to="/config/rate-limit" className="text-caption text-[var(--theme-accent)] hover:underline flex items-center gap-1 mt-1">
                Editar <ExternalLink size={10} />
              </Link>
            </div>
            <div>
              <span className="text-caption text-[var(--theme-text-secondary)] flex items-center gap-1">
                <FolderOutput size={12} /> Saida
              </span>
              <p className="text-mono font-medium text-[var(--theme-text)] truncate" title={config.diretorio_saida}>
                {config.diretorio_saida}
              </p>
              <Link to="/config/saida" className="text-caption text-[var(--theme-accent)] hover:underline flex items-center gap-1 mt-1">
                Editar <ExternalLink size={10} />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Grid: metrics + console */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Metrics */}
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-h4 text-[var(--theme-text)]">Status</h3>
              {executionStatus && (
                <Badge variant={executionStatus.variant}>{executionStatus.label}</Badge>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-caption text-[var(--theme-text-secondary)]">Token ativo</span>
                <p className="text-mono font-medium text-[var(--theme-text)]">
                  {status?.token_ativo?.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase()) ?? "--"}
                </p>
              </div>
              <div>
                <span className="text-caption text-[var(--theme-text-secondary)]">Endpoint</span>
                <p className="text-mono font-medium text-[var(--theme-text)] capitalize">
                  {status?.endpoint_atual ?? "--"}
                </p>
              </div>
              <div>
                <span className="text-caption text-[var(--theme-text-secondary)]">Periodo</span>
                <p className="text-mono font-medium text-[var(--theme-text)]">
                  {status?.ano_mes_atual ?? "--"}
                </p>
              </div>
              <div>
                <span className="text-caption text-[var(--theme-text-secondary)]">Pagina</span>
                <p className="text-mono font-medium text-[var(--theme-text)]">
                  {status?.pagina_atual ?? 0}
                </p>
              </div>
              <div className="col-span-2">
                <span className="text-caption text-[var(--theme-text-secondary)]">Total de registros</span>
                <p className="text-h3 font-mono text-[var(--theme-text)]">
                  {(status?.total_registros ?? 0).toLocaleString("pt-BR")}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-h4 text-[var(--theme-text)] mb-3">Req/min</h3>
            <Gauge
              value={status?.req_minuto ?? 0}
              max={reqMax}
              variant="horizontal"
            />
          </div>
        </div>

        {/* Console */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-h4 text-[var(--theme-text)]">Console</h3>
            <button
              className="text-caption text-[var(--theme-text-secondary)] hover:text-[var(--theme-text)] transition-colors cursor-pointer"
              onClick={() => {
                setConsoleLogs([]);
                localStorage.removeItem("execucao_console_logs");
              }}
            >
              Limpar
            </button>
          </div>
          <div ref={consoleRef} className="console h-[400px]">
            {consoleLogs.length === 0 ? (
              <span className="text-[var(--theme-text-secondary)]">Aguardando inicio do download...</span>
            ) : (
              consoleLogs.map((log, i) => (
                <div key={i} className={`log-${log.level}`}>
                  <span className="text-[#737373]">[{log.timestamp}]</span> {log.message}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <ConfirmDialog
        open={showStopDialog}
        title="Parar Download"
        message="Deseja parar o download em andamento? O progresso sera salvo."
        confirmLabel="Parar Download"
        cancelLabel="Cancelar"
        onConfirm={confirmStop}
        onCancel={() => setShowStopDialog(false)}
      />
    </div>
  );
}
