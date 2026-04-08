import { MonitorDot, Clock } from "lucide-react";

import { useWebSocket } from "@/hooks/useWebSocket";
import { TokenCard } from "@/components/ui/TokenCard";
import { Badge } from "@/components/ui/Badge";

function getTimeBand(): { label: string; variant: "info" | "warning" | "success" } {
  const now = new Date();
  const brHour = new Date(now.toLocaleString("en-US", { timeZone: "America/Sao_Paulo" })).getHours();
  if (brHour >= 0 && brHour < 6) {
    return { label: `Madrugada (${brHour}h BRT) - Limite maior`, variant: "success" };
  }
  return { label: `Dia (${brHour}h BRT) - Limite padrao`, variant: "info" };
}

export function MonitorTokens() {
  const { status, connected } = useWebSocket();
  const timeBand = getTimeBand();

  return (
    <div>
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <MonitorDot size={24} /> Monitor de Tokens
      </h2>

      {/* Time band indicator */}
      <div className="card mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Clock size={18} style={{ color: "var(--theme-text-secondary)" }} />
          <div>
            <span className="text-body text-[var(--theme-text)]">Faixa horaria ativa</span>
            <div className="mt-1">
              <Badge variant={timeBand.variant}>{timeBand.label}</Badge>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-[var(--theme-success)]" : "bg-[var(--theme-error)]"}`} />
          <span className="text-caption text-[var(--theme-text-secondary)]">
            WebSocket: {connected ? "Conectado" : "Desconectado"}
          </span>
        </div>
      </div>

      {/* Token cards grid */}
      {status?.token_statuses && status.token_statuses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {status.token_statuses.map((token) => (
            <TokenCard key={token.token_id} token={token} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-body text-[var(--theme-text-secondary)]">
            Nenhum token ativo no momento. Inicie um download para monitorar os tokens.
          </p>
        </div>
      )}
    </div>
  );
}
