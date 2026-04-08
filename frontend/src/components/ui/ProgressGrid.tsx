import type { DownloadProgress, EndpointType } from "@/types";

interface Props {
  items: DownloadProgress[];
  endpoint?: EndpointType | "todos";
}

const MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

const statusColors: Record<string, string> = {
  concluido: "#16a34a",
  arquivo_ausente: "#eab308",
  em_andamento: "#3b82f6",
  erro: "#dc2626",
  pendente: "#dc2626",
};

const statusLabels: Record<string, string> = {
  concluido: "Concluido",
  arquivo_ausente: "Baixado (arquivo ausente na pasta)",
  em_andamento: "Parcial (incompleto)",
  erro: "Erro",
  pendente: "Nao baixado",
};

export function ProgressGrid({ items, endpoint }: Props) {
  const filtered = endpoint && endpoint !== "todos"
    ? items.filter((i) => i.endpoint === endpoint)
    : items;

  if (filtered.length === 0) {
    return (
      <p className="text-body text-[var(--theme-text-secondary)]">
        Nenhum progresso registrado para os filtros selecionados.
      </p>
    );
  }

  const years = [...new Set(filtered.map((i) => i.ano))].sort();
  const lookup = new Map(filtered.map((i) => [`${i.endpoint}-${i.ano}-${i.mes}`, i]));

  const endpoints = endpoint && endpoint !== "todos"
    ? [endpoint]
    : [...new Set(filtered.map((i) => i.endpoint))].sort();

  return (
    <div className="space-y-8">
      {endpoints.map((ep) => (
        <div key={ep}>
          <h3 className="text-h4 text-[var(--theme-text)] mb-4 capitalize">{ep}</h3>
          <div className="overflow-x-auto">
            <div className="inline-grid" style={{ gridTemplateColumns: `80px repeat(12, 48px)`, gap: "4px" }}>
              <div />
              {MONTHS.map((m) => (
                <div key={m} className="text-caption text-center text-[var(--theme-text-secondary)] font-medium">
                  {m}
                </div>
              ))}

              {years.map((year) => (
                <div key={year} className="contents">
                  <div className="text-caption font-mono font-medium text-[var(--theme-text)] flex items-center">
                    {year}
                  </div>
                  {Array.from({ length: 12 }, (_, i) => {
                    const item = lookup.get(`${ep}-${year}-${i + 1}`);
                    const status = item?.status ?? "pendente";
                    const color = statusColors[status] ?? statusColors.pendente;
                    const icon = status === "concluido"
                      ? "\u2713"
                      : status === "arquivo_ausente"
                      ? "\u26A0"
                      : status === "erro"
                      ? "!"
                      : status === "em_andamento"
                      ? "\u2026"
                      : "";
                    return (
                      <div
                        key={i}
                        className="w-12 h-12 rounded flex items-center justify-center text-xs font-mono cursor-default transition-opacity hover:opacity-80"
                        style={{ backgroundColor: color, opacity: status === "pendente" ? 0.6 : 1 }}
                        title={`${ep} ${year}/${String(i + 1).padStart(2, "0")} - ${statusLabels[status] ?? "Pendente"}${item ? ` (${item.total_registros.toLocaleString()} reg.)` : ""}${item && status === "em_andamento" && item.ultima_pagina > 0 ? ` | Ultima pg: ${item.ultima_pagina}` : ""}`}
                      >
                        {icon && (
                          <span className="text-white text-[10px] font-bold">
                            {icon}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}

      <div className="flex flex-wrap items-center gap-6 mt-4">
        {Object.entries(statusLabels).map(([key, label]) => (
          <div key={key} className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: statusColors[key] }}
            />
            <span className="text-caption text-[var(--theme-text-secondary)]">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
