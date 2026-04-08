import { useState } from "react";
import { BarChart3, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { progressApi } from "@/api/endpoints";
import { ProgressGrid } from "@/components/ui/ProgressGrid";
import { Gauge } from "@/components/ui/Gauge";

export function Progresso() {
  const [filtroEndpoint, setFiltroEndpoint] = useState<"todos" | "despesas" | "receitas">("todos");
  const [filtroAno, setFiltroAno] = useState<number | undefined>(undefined);
  const [exibirPendentes, setExibirPendentes] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["progress", filtroEndpoint, filtroAno, exibirPendentes],
    queryFn: () =>
      progressApi.get({
        filtro_endpoint: filtroEndpoint !== "todos" ? filtroEndpoint : undefined,
        filtro_ano: filtroAno,
        exibir_apenas_pendentes: exibirPendentes || undefined,
      }),
  });

  const items = data?.items ?? [];
  const stats = {
    arquivos: data?.total_arquivos_gerados ?? 0,
    tamanho: data?.tamanho_total_disco ?? 0,
    percentual: data?.percentual_concluido ?? 0,
  };

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-[var(--theme-text-secondary)]">
        <Loader2 size={18} className="animate-spin" /> Carregando progresso...
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <BarChart3 size={24} /> Progresso de Downloads
      </h2>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Endpoint</label>
            <select
              className="input-base !h-9 text-sm"
              value={filtroEndpoint}
              onChange={(e) => setFiltroEndpoint(e.target.value as "todos" | "despesas" | "receitas")}
            >
              <option value="todos">Todos</option>
              <option value="despesas">Despesas</option>
              <option value="receitas">Receitas</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Ano</label>
            <input
              type="number"
              min={2004}
              max={2026}
              placeholder="Todos"
              className="input-base !h-9 text-sm font-mono w-28"
              value={filtroAno ?? ""}
              onChange={(e) => setFiltroAno(e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer pb-1">
            <input
              type="checkbox"
              checked={exibirPendentes}
              onChange={(e) => setExibirPendentes(e.target.checked)}
              className="w-4 h-4 accent-[var(--theme-accent)]"
            />
            <span className="text-body text-[var(--theme-text)]">Apenas pendentes</span>
          </label>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="card text-center">
          <span className="text-caption text-[var(--theme-text-secondary)]">Arquivos gerados</span>
          <p className="text-h2 font-mono text-[var(--theme-text)]">{stats.arquivos.toLocaleString()}</p>
        </div>
        <div className="card text-center">
          <span className="text-caption text-[var(--theme-text-secondary)]">Tamanho total</span>
          <p className="text-h2 font-mono text-[var(--theme-text)]">{formatSize(stats.tamanho)}</p>
        </div>
        <div className="card text-center">
          <span className="text-caption text-[var(--theme-text-secondary)]">Progresso geral</span>
          <p className="text-h2 font-mono text-[var(--theme-text)]">{stats.percentual.toFixed(1)}%</p>
        </div>
      </div>

      {/* Calendar grid */}
      <div className="card">
        <ProgressGrid items={items} endpoint={filtroEndpoint} />
      </div>

      {/* Overall progress bar */}
      <div className="card mt-6">
        <Gauge
          value={stats.percentual}
          max={100}
          label="Progresso geral"
          variant="horizontal"
        />
      </div>
    </div>
  );
}
