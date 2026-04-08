import { NavLink } from "react-router-dom";
import {
  Key,
  Calendar,
  Gauge,
  Globe,
  FolderOutput,
  Play,
  MonitorDot,
  FileText,
  BarChart3,
  RotateCcw,
  Sun,
  Moon,
  Monitor,
  X,
  Cpu,
  MessageSquare,
} from "lucide-react";
import { clsx } from "clsx";

import { useTheme } from "../../hooks/useTheme";

interface Props {
  open: boolean;
  onClose: () => void;
}

const configItems = [
  { label: "Tokens", path: "/config/tokens", icon: Key },
  { label: "Periodo", path: "/config/periodo", icon: Calendar },
  { label: "Rate Limit", path: "/config/rate-limit", icon: Gauge },
  { label: "Endpoints", path: "/config/endpoints", icon: Globe },
  { label: "Saida", path: "/config/saida", icon: FolderOutput },
  { label: "IA (Agentes)", path: "/config/ia", icon: Cpu },
];

const operationItems = [
  { label: "Progresso", path: "/progresso", icon: BarChart3 },
  { label: "Execucao", path: "/execucao", icon: Play },
  { label: "Monitor Tokens", path: "/monitor/tokens", icon: MonitorDot },
  { label: "Logs", path: "/logs", icon: FileText },
  { label: "Retomada", path: "/retomada", icon: RotateCcw },
  { label: "Chat Auditoria", path: "/chat", icon: MessageSquare },
];

const themeOptions = [
  { value: "light" as const, icon: Sun, label: "Claro" },
  { value: "dark" as const, icon: Moon, label: "Escuro" },
  { value: "system" as const, icon: Monitor, label: "Sistema" },
];

function NavItem({ item, onClick }: { item: (typeof configItems)[0]; onClick?: () => void }) {
  return (
    <NavLink
      to={item.path}
      onClick={onClick}
      className={({ isActive }) =>
        clsx(
          "flex items-center gap-3 px-4 py-2.5 text-sm transition-colors",
          isActive
            ? "bg-white/10 text-white font-medium"
            : "text-white/60 hover:text-white hover:bg-white/5",
        )
      }
    >
      <item.icon size={18} />
      {item.label}
    </NavLink>
  );
}

export function Sidebar({ open, onClose }: Props) {
  const { theme, setTheme } = useTheme();

  const sidebarContent = (
    <aside
      className={clsx(
        "w-60 h-screen flex flex-col fixed left-0 top-0 z-50",
        "transition-transform duration-200 lg:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full",
      )}
      style={{ background: "var(--theme-gradient-header)" }}
    >
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <h1 className="text-sm font-bold tracking-wide uppercase text-white">
          Base Transparencia
        </h1>
        <button
          onClick={onClose}
          className="lg:hidden text-white/60 hover:text-white transition-colors"
          aria-label="Fechar menu"
        >
          <X size={20} />
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        <div className="px-4 py-2">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-white/40">
            Operacao
          </span>
        </div>
        {operationItems.map((item) => (
          <NavItem key={item.path} item={item} onClick={onClose} />
        ))}

        <div className="px-4 py-2 mt-2">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-white/40">
            Configuracao
          </span>
        </div>
        {configItems.map((item) => (
          <NavItem key={item.path} item={item} onClick={onClose} />
        ))}
      </nav>

      <div className="p-3 border-t border-white/10">
        <div className="flex items-center justify-between rounded-md bg-white/5 p-1">
          {themeOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setTheme(opt.value)}
              title={opt.label}
              className={clsx(
                "flex-1 flex items-center justify-center gap-1 rounded px-2 py-1.5 text-xs transition-colors",
                theme === opt.value
                  ? "bg-white/15 text-white"
                  : "text-white/50 hover:text-white/80",
              )}
            >
              <opt.icon size={14} />
            </button>
          ))}
        </div>
      </div>
    </aside>
  );

  return (
    <>
      {open && (
        <div
          className="sidebar-overlay lg:hidden"
          onClick={onClose}
        />
      )}
      {sidebarContent}
    </>
  );
}
