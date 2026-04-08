import { useState } from "react";
import { FileText, Search, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";

import { useLogs } from "@/hooks/useLogs";
import { logFiltersSchema, type LogFiltersFormData } from "@/schemas";
import { Badge } from "@/components/ui/Badge";
import type { LogFilters, LogLevel } from "@/types";

const ITEMS_PER_PAGE = 50;

const levelConfig: Record<string, { variant: "info" | "warning" | "error"; label: string }> = {
  info: { variant: "info", label: "Info" },
  warning: { variant: "warning", label: "Warning" },
  error: { variant: "error", label: "Error" },
};

export function Logs() {
  const [filters, setFilters] = useState<LogFiltersFormData>({
    filtro_data_inicio: "",
    filtro_data_fim: "",
    filtro_nivel_log: "todos",
    filtro_endpoint: "todos",
    filtro_token: "todos",
    busca_texto: "",
    limit: ITEMS_PER_PAGE,
    offset: 0,
  });
  const [filterErrors, setFilterErrors] = useState<Record<string, string>>({});

  const apiFilters: LogFilters = {
    ...(filters.filtro_data_inicio ? { filtro_data_inicio: filters.filtro_data_inicio } : {}),
    ...(filters.filtro_data_fim ? { filtro_data_fim: filters.filtro_data_fim } : {}),
    ...(filters.filtro_nivel_log && filters.filtro_nivel_log !== "todos" ? { filtro_nivel_log: filters.filtro_nivel_log as LogLevel } : {}),
    ...(filters.filtro_endpoint && filters.filtro_endpoint !== "todos" ? { filtro_endpoint: filters.filtro_endpoint as "despesas" | "receitas" } : {}),
    ...(filters.filtro_token && filters.filtro_token !== "todos" ? { filtro_token: filters.filtro_token as "token_1" | "token_2" | "token_3" } : {}),
    ...(filters.busca_texto ? { busca_texto: filters.busca_texto } : {}),
    limit: ITEMS_PER_PAGE,
    offset: filters.offset,
  };

  const { data, isLoading } = useLogs(apiFilters);
  const logs = data?.items ?? [];
  const total = data?.total ?? 0;
  const currentPage = Math.floor((filters.offset ?? 0) / ITEMS_PER_PAGE) + 1;
  const totalPages = Math.max(1, Math.ceil(total / ITEMS_PER_PAGE));

  function handleFilterChange(field: string, value: string) {
    setFilters((prev) => ({ ...prev, [field]: value, offset: 0 }));
    setFilterErrors((prev) => { const n = { ...prev }; delete n[field]; return n; });
  }

  function handleSearch() {
    const result = logFiltersSchema.safeParse(filters);
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const path = issue.path.join(".");
        if (!fieldErrors[path]) fieldErrors[path] = issue.message;
      }
      setFilterErrors(fieldErrors);
    } else {
      setFilterErrors({});
    }
  }

  function goToPage(page: number) {
    setFilters((prev) => ({ ...prev, offset: (page - 1) * ITEMS_PER_PAGE }));
  }

  return (
    <div>
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <FileText size={24} /> Visualizador de Logs
      </h2>

      {/* Filter bar */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Data inicio</label>
            <input
              type="date"
              className={`input-base !h-9 text-sm ${filterErrors["filtro_data_inicio"] ? "input-error" : ""}`}
              value={filters.filtro_data_inicio ?? ""}
              onChange={(e) => handleFilterChange("filtro_data_inicio", e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Data fim</label>
            <input
              type="date"
              className={`input-base !h-9 text-sm ${filterErrors["filtro_data_fim"] ? "input-error" : ""}`}
              value={filters.filtro_data_fim ?? ""}
              onChange={(e) => handleFilterChange("filtro_data_fim", e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Nivel</label>
            <select
              className="input-base !h-9 text-sm"
              value={filters.filtro_nivel_log ?? "todos"}
              onChange={(e) => handleFilterChange("filtro_nivel_log", e.target.value)}
            >
              <option value="todos">Todos</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Endpoint</label>
            <select
              className="input-base !h-9 text-sm"
              value={filters.filtro_endpoint ?? "todos"}
              onChange={(e) => handleFilterChange("filtro_endpoint", e.target.value)}
            >
              <option value="todos">Todos</option>
              <option value="despesas">Despesas</option>
              <option value="receitas">Receitas</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-caption text-[var(--theme-text-secondary)]">Token</label>
            <select
              className="input-base !h-9 text-sm"
              value={filters.filtro_token ?? "todos"}
              onChange={(e) => handleFilterChange("filtro_token", e.target.value)}
            >
              <option value="todos">Todos</option>
              <option value="token_1">Token 1</option>
              <option value="token_2">Token 2</option>
              <option value="token_3">Token 3</option>
            </select>
          </div>
          <div className="space-y-1 flex-1 min-w-[200px]">
            <label className="text-caption text-[var(--theme-text-secondary)]">Busca</label>
            <div className="relative">
              <input
                type="text"
                className={`input-base !h-9 text-sm pr-9 ${filterErrors["busca_texto"] ? "input-error" : ""}`}
                placeholder="Buscar na mensagem (min. 3 caracteres)"
                value={filters.busca_texto ?? ""}
                onChange={(e) => handleFilterChange("busca_texto", e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
              <Search size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--theme-text-secondary)]" />
            </div>
            {filterErrors["busca_texto"] && (
              <p className="text-caption text-[var(--theme-error)]">{filterErrors["busca_texto"]}</p>
            )}
          </div>
        </div>
        {filterErrors["filtro_data_fim"] && (
          <p className="text-caption text-[var(--theme-error)] mt-2">{filterErrors["filtro_data_fim"]}</p>
        )}
      </div>

      {/* Table */}
      <div className="card !p-0 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center gap-2 p-8 text-[var(--theme-text-secondary)]">
            <Loader2 size={18} className="animate-spin" /> Carregando logs...
          </div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-[var(--theme-text-secondary)]">
            Nenhum log encontrado para os filtros aplicados.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--theme-surface-2)" }}>
                  <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)] whitespace-nowrap">Timestamp</th>
                  <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Nivel</th>
                  <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Token</th>
                  <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Endpoint</th>
                  <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">HTTP</th>
                  <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Mensagem</th>
                </tr>
              </thead>
              <tbody className="table-zebra">
                {logs.map((log) => {
                  const level = levelConfig[log.nivel] ?? levelConfig.info;
                  return (
                    <tr key={log.id} style={{ borderTop: "1px solid var(--theme-border)" }}>
                      <td className="px-4 py-2 font-mono text-xs whitespace-nowrap text-[var(--theme-text)]">{log.timestamp}</td>
                      <td className="px-4 py-2">
                        <Badge variant={level.variant}>{level.label}</Badge>
                      </td>
                      <td className="px-4 py-2 font-mono text-xs text-[var(--theme-text-secondary)]">{log.token_id ?? "-"}</td>
                      <td className="px-4 py-2 text-xs text-[var(--theme-text-secondary)] capitalize">{log.endpoint ?? "-"}</td>
                      <td className="px-4 py-2 font-mono text-xs text-[var(--theme-text-secondary)]">{log.status_http ?? "-"}</td>
                      <td className="px-4 py-2 text-xs text-[var(--theme-text)]">{log.mensagem}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {total > ITEMS_PER_PAGE && (
          <div className="flex items-center justify-between px-4 py-3 border-t" style={{ borderColor: "var(--theme-border)" }}>
            <span className="text-caption text-[var(--theme-text-secondary)]">
              {total.toLocaleString()} logs encontrados
            </span>
            <div className="flex items-center gap-2">
              <button
                className="btn btn-secondary !h-8 !px-2"
                disabled={currentPage <= 1}
                onClick={() => goToPage(currentPage - 1)}
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-caption text-[var(--theme-text)]">
                {currentPage} / {totalPages}
              </span>
              <button
                className="btn btn-secondary !h-8 !px-2"
                disabled={currentPage >= totalPages}
                onClick={() => goToPage(currentPage + 1)}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
