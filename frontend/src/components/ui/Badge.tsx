import { clsx } from "clsx";

interface Props {
  variant: "success" | "warning" | "error" | "info" | "orange";
  children: React.ReactNode;
  className?: string;
}

const variantClasses = {
  success: "badge-success",
  warning: "badge-warning",
  error: "badge-error",
  info: "badge-info",
  orange: "badge-orange",
};

export function Badge({ variant, children, className }: Props) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium",
        variantClasses[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
