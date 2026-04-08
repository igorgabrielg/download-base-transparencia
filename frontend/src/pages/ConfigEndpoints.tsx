import { useState, useEffect } from "react";
import { Globe, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

import { useConfig, useUpdateEndpoints } from "@/hooks/useConfig";
import { configEndpointsRequestSchema, type ConfigEndpointsFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";

export function ConfigEndpoints() {
  const { data: config, isLoading } = useConfig();
  const updateEndpoints = useUpdateEndpoints();

  const [form, setForm] = useState<ConfigEndpointsFormData>({
    baixar_despesas: true,
    baixar_receitas: true,
    base_url: "https://api.portaldatransparencia.gov.br/api-de-dados",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setForm({
        baixar_despesas: config.baixar_despesas,
        baixar_receitas: config.baixar_receitas,
        base_url: config.base_url,
      });
    }
  }, [config]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = configEndpointsRequestSchema.safeParse(form);
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
    updateEndpoints.mutate(result.data, {
      onSuccess: () => toast.success("Endpoints salvos com sucesso."),
      onError: () => toast.error("Nao foi possivel salvar os endpoints."),
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
        <Globe size={24} /> Selecao de Endpoints
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Escolha quais conjuntos de dados deseja baixar e a URL base da API.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <h3 className="text-h4 text-[var(--theme-text)]">Dados para Download</h3>
        {errors["baixar_despesas"] && (
          <p className="text-caption text-[var(--theme-error)]">{errors["baixar_despesas"]}</p>
        )}

        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.baixar_despesas}
              onChange={(e) => {
                setForm((prev) => ({ ...prev, baixar_despesas: e.target.checked }));
                setErrors((prev) => { const n = { ...prev }; delete n["baixar_despesas"]; return n; });
              }}
              className="w-5 h-5 rounded accent-[var(--theme-accent)]"
            />
            <div>
              <span className="text-body font-medium text-[var(--theme-text)]">Despesas</span>
              <p className="text-caption text-[var(--theme-text-secondary)]">
                Dados de despesas publicas do Portal da Transparencia.
              </p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.baixar_receitas}
              onChange={(e) => {
                setForm((prev) => ({ ...prev, baixar_receitas: e.target.checked }));
                setErrors((prev) => { const n = { ...prev }; delete n["baixar_despesas"]; return n; });
              }}
              className="w-5 h-5 rounded accent-[var(--theme-accent)]"
            />
            <div>
              <span className="text-body font-medium text-[var(--theme-text)]">Receitas</span>
              <p className="text-caption text-[var(--theme-text-secondary)]">
                Dados de receitas publicas do Portal da Transparencia.
              </p>
            </div>
          </label>
        </div>

        <h3 className="text-h4 text-[var(--theme-text)]">URL Base da API</h3>

        <FormField
          label="URL base"
          required
          error={errors["base_url"]}
          htmlFor="base_url"
          hint="URL deve iniciar com http:// ou https://"
        >
          <input
            id="base_url"
            type="text"
            className={`input-base font-mono ${errors["base_url"] ? "input-error" : ""}`}
            placeholder="https://api.portaldatransparencia.gov.br/api-de-dados"
            value={form.base_url}
            onChange={(e) => {
              setForm((prev) => ({ ...prev, base_url: e.target.value }));
              setErrors((prev) => { const n = { ...prev }; delete n["base_url"]; return n; });
            }}
          />
        </FormField>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={updateEndpoints.isPending}
          >
            {updateEndpoints.isPending ? (
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
