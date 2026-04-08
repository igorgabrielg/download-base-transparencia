import { Badge } from "./Badge";
import { Gauge } from "./Gauge";
import type { TokenStatus } from "@/types";

interface Props {
  token: TokenStatus;
}

const statusConfig: Record<string, { variant: "success" | "warning" | "error" | "orange" | "info"; label: string }> = {
  ativo: { variant: "success", label: "Ativo" },
  em_espera: { variant: "warning", label: "Em espera" },
  invalido: { variant: "error", label: "Invalido" },
  limite_atingido: { variant: "orange", label: "Limite atingido" },
};

function formatTokenId(id: string): string {
  return id.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatTimer(seconds: number): string {
  if (seconds <= 0) return "--";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

export function TokenCard({ token }: Props) {
  const config = statusConfig[token.status] ?? { variant: "info" as const, label: token.status };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <span className="text-h5 font-mono">{formatTokenId(token.token_id)}</span>
        <Badge variant={config.variant}>{config.label}</Badge>
      </div>

      <div className="mb-4">
        <Gauge
          value={token.req_minuto_atual}
          max={token.limite_aplicavel}
          label="Req/min"
        />
      </div>

      <div className="flex items-center justify-between text-caption text-[var(--theme-text-secondary)]">
        <span>Reset em</span>
        <span className="font-mono font-medium text-[var(--theme-text)]">
          {formatTimer(token.tempo_para_reset)}
        </span>
      </div>
    </div>
  );
}
