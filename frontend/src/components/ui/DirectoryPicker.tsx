import { useState } from "react";
import { FolderOpen, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

import { configApi } from "@/api/endpoints";

interface Props {
  value: string;
  onChange: (path: string) => void;
  label: string;
}

export function DirectoryPicker({ value, onChange, label }: Props) {
  const [loading, setLoading] = useState(false);

  async function handlePick() {
    setLoading(true);
    try {
      const res = await configApi.pickDirectory();
      if (res.path) {
        onChange(res.path);
      } else if (res.error) {
        toast.error(res.error);
      }
    } catch {
      toast.error("Erro ao abrir seletor de pasta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <input
        type="text"
        className="input-base font-mono flex-1"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Ex: /home/user/dados"
      />
      <button
        type="button"
        className="btn btn-secondary whitespace-nowrap"
        onClick={handlePick}
        disabled={loading}
      >
        {loading ? <Loader2 size={16} className="animate-spin" /> : <FolderOpen size={16} />}
        {loading ? "Abrindo..." : "Procurar"}
      </button>
    </div>
  );
}
