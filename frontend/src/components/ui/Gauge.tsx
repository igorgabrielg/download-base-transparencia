import { clsx } from "clsx";

interface Props {
  value: number;
  max: number;
  label?: string;
  variant?: "circular" | "horizontal";
  showValue?: boolean;
}

export function Gauge({ value, max, label, variant = "horizontal", showValue = true }: Props) {
  const percentage = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  const semanticColor =
    percentage < 70
      ? "var(--theme-success)"
      : percentage < 90
        ? "var(--theme-warning)"
        : "var(--theme-error)";

  if (variant === "circular") {
    return (
      <div className="flex flex-col items-center gap-1">
        <div className="relative w-20 h-20">
          <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="var(--theme-border)"
              strokeWidth="3"
            />
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke={semanticColor}
              strokeWidth="3"
              strokeDasharray={`${percentage}, 100`}
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-xs font-mono font-bold text-[var(--theme-text)]">
            {Math.round(percentage)}%
          </span>
        </div>
        {label && <span className="text-caption text-[var(--theme-text-secondary)]">{label}</span>}
      </div>
    );
  }

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1">
          {label && <span className="text-caption text-[var(--theme-text-secondary)]">{label}</span>}
          {showValue && (
            <span className="text-mono font-medium text-[var(--theme-text)]">
              {value} / {max}
            </span>
          )}
        </div>
      )}
      <div
        className={clsx("h-2.5 rounded-full overflow-hidden")}
        style={{ backgroundColor: "var(--theme-surface-3)" }}
      >
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{ width: `${percentage}%`, backgroundColor: semanticColor }}
        />
      </div>
    </div>
  );
}
