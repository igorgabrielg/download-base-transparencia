import { useState, useEffect } from "react";
import { FolderOutput, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

import { useConfig, useUpdateSaida } from "@/hooks/useConfig";
import { configSaidaRequestSchema, type ConfigSaidaFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";
import { DirectoryPicker } from "@/components/ui/DirectoryPicker";

export function ConfigSaida() {
  const { data: config, isLoading } = useConfig();
  const updateSaida = useUpdateSaida();

  const [form, setForm] = useState<ConfigSaidaFormData>({
    diretorio_saida: "",
    diretorio_logs: "",
    formato_nome_arquivo: "por_ano_mes",
    modo_escrita: "append",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setForm({
        diretorio_saida: config.diretorio_saida,
        diretorio_logs: config.diretorio_logs,
        formato_nome_arquivo: config.formato_nome_arquivo,
        modo_escrita: config.modo_escrita,
      });
    }
  }, [config]);

  function handleChange(field: keyof ConfigSaidaFormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = configSaidaRequestSchema.safeParse(form);
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const path = issue.path.join(".");
        if (!fieldErrors[path]) fieldErrors[path] = issue.message;
      }
      setErrors(fieldErrors);
      return;
    }
    setErrors({});
    updateSaida.mutate(result.data, {
      onSuccess: () => toast.success("Configuracao de saida salva com sucesso."),
      onError: () => toast.error("Nao foi possivel salvar a configuracao de saida."),
    });
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-[var(--theme-text-secondary)]">
        <Loader2 size={18} className="animate-spin" /> Carregando configuracao...
      </div>
    );
  }

  return (
    <div className="page-config">
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <FolderOutput size={24} /> Configuracao de Saida
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Defina onde os arquivos serao salvos. Alem dos CSVs, um banco SQLite (<code className="font-mono text-sm">transparencia.db</code>) e gerado automaticamente no diretorio de saida para facilitar consultas por outras pessoas.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <h3 className="text-h4 text-[var(--theme-text)]">Diretorios</h3>

        <FormField
          label="Diretorio de saida"
          required
          error={errors["diretorio_saida"]}
          htmlFor="diretorio_saida"
          hint="Caminho onde os arquivos CSV e o banco SQLite serao salvos."
        >
          <DirectoryPicker
            value={form.diretorio_saida}
            onChange={(path) => handleChange("diretorio_saida", path)}
            label="Diretorio de saida"
          />
        </FormField>

        <FormField
          label="Diretorio de logs"
          required
          error={errors["diretorio_logs"]}
          htmlFor="diretorio_logs"
          hint="Caminho onde os arquivos de log serao salvos."
        >
          <DirectoryPicker
            value={form.diretorio_logs}
            onChange={(path) => handleChange("diretorio_logs", path)}
            label="Diretorio de logs"
          />
        </FormField>

        <h3 className="text-h4 text-[var(--theme-text)]">Formato de Arquivo</h3>

        <FormField
          label="Nome do arquivo"
          error={errors["formato_nome_arquivo"]}
          htmlFor="formato_nome_arquivo"
        >
          <select
            id="formato_nome_arquivo"
            className={`input-base ${errors["formato_nome_arquivo"] ? "input-error" : ""}`}
            value={form.formato_nome_arquivo}
            onChange={(e) => handleChange("formato_nome_arquivo", e.target.value)}
          >
            <option value="por_ano_mes">Por ano e mes (despesas_2024_01.csv)</option>
            <option value="por_ano">Por ano (despesas_2024.csv)</option>
          </select>
        </FormField>

        <FormField
          label="Modo de escrita"
          error={errors["modo_escrita"]}
          htmlFor="modo_escrita"
          hint="Append adiciona dados ao arquivo existente. Overwrite substitui o conteudo."
        >
          <select
            id="modo_escrita"
            className={`input-base ${errors["modo_escrita"] ? "input-error" : ""}`}
            value={form.modo_escrita}
            onChange={(e) => handleChange("modo_escrita", e.target.value)}
          >
            <option value="append">Append (adicionar ao existente)</option>
            <option value="overwrite">Overwrite (substituir)</option>
          </select>
        </FormField>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={updateSaida.isPending}
          >
            {updateSaida.isPending ? (
              <><Loader2 size={16} className="animate-spin" /> Salvando...</>
            ) : (
              "Salvar Configuracao"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
