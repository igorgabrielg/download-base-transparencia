import { clsx } from "clsx";

interface Props {
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
  htmlFor?: string;
}

export function FormField({ label, error, hint, required, children, htmlFor }: Props) {
  return (
    <div className="space-y-1">
      <label
        htmlFor={htmlFor}
        className={clsx("block text-body font-medium", error ? "text-[var(--theme-error)]" : "text-[var(--theme-text)]")}
      >
        {label}
        {required && <span className="text-[var(--theme-error)] ml-0.5">*</span>}
      </label>
      {children}
      {error && <p className="text-caption text-[var(--theme-error)]">{error}</p>}
      {!error && hint && <p className="text-caption text-[var(--theme-text-secondary)]">{hint}</p>}
    </div>
  );
}
