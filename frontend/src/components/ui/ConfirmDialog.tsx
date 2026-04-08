import { AlertTriangle } from "lucide-react";

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  onConfirm,
  onCancel,
}: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="sidebar-overlay" onClick={onCancel} />
      <div className="card relative z-10 max-w-sm w-full mx-4 shadow-lg">
        <div className="flex items-start gap-3 mb-4">
          <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center badge-warning">
            <AlertTriangle size={20} />
          </div>
          <div>
            <h3 className="text-h4 text-[var(--theme-text)]">{title}</h3>
            <p className="text-body text-[var(--theme-text-secondary)] mt-1">{message}</p>
          </div>
        </div>
        <div className="flex justify-end gap-3">
          <button className="btn btn-secondary" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button className="btn btn-danger" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
