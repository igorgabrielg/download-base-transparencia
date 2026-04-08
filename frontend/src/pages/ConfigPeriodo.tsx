import { useState, useEffect } from "react";
import { Calendar, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

import { useConfig, useUpdatePeriodo } from "@/hooks/useConfig";
import { configPeriodoRequestSchema, type ConfigPeriodoFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";

const MONTHS = [
  { value: 1, label: "Janeiro" },
  { value: 2, label: "Fevereiro" },
  { value: 3, label: "Marco" },
  { value: 4, label: "Abril" },
  { value: 5, label: "Maio" },
  { value: 6, label: "Junho" },
  { value: 7, label: "Julho" },
  { value: 8, label: "Agosto" },
  { value: 9, label: "Setembro" },
  { value: 10, label: "Outubro" },
  { value: 11, label: "Novembro" },
  { value: 12, label: "Dezembro" },
];

export function ConfigPeriodo() {
  const { data: config, isLoading } = useConfig();
  const updatePeriodo = useUpdatePeriodo();

  const [form, setForm] = useState<ConfigPeriodoFormData>({
    ano_inicio: 2024,
    ano_fim: 2026,
    mes_inicio: 1,
    mes_fim: 12,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setForm({
        ano_inicio: config.ano_inicio,
        ano_fim: config.ano_fim,
        mes_inicio: config.mes_inicio,
        mes_fim: config.mes_fim,
      });
    }
  }, [config]);

  function handleChange(field: keyof ConfigPeriodoFormData, value: number) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = configPeriodoRequestSchema.safeParse(form);
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
    updatePeriodo.mutate(result.data, {
      onSuccess: () => toast.success("Periodo salvo com sucesso."),
      onError: () => toast.error("Nao foi possivel salvar o periodo."),
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
        <Calendar size={24} /> Configuracao de Periodo
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Defina o intervalo de anos e meses para download dos dados.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <h3 className="text-h4 text-[var(--theme-text)]">Ano</h3>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Ano inicio" required error={errors["ano_inicio"]} htmlFor="ano_inicio">
            <input
              id="ano_inicio"
              type="number"
              min={2004}
              max={2026}
              className={`input-base font-mono ${errors["ano_inicio"] ? "input-error" : ""}`}
              value={form.ano_inicio}
              onChange={(e) => handleChange("ano_inicio", Number(e.target.value))}
            />
          </FormField>
          <FormField label="Ano fim" required error={errors["ano_fim"]} htmlFor="ano_fim">
            <input
              id="ano_fim"
              type="number"
              min={2004}
              max={2026}
              className={`input-base font-mono ${errors["ano_fim"] ? "input-error" : ""}`}
              value={form.ano_fim}
              onChange={(e) => handleChange("ano_fim", Number(e.target.value))}
            />
          </FormField>
        </div>

        <h3 className="text-h4 text-[var(--theme-text)]">Mes</h3>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Mes inicio" error={errors["mes_inicio"]} htmlFor="mes_inicio">
            <select
              id="mes_inicio"
              className={`input-base ${errors["mes_inicio"] ? "input-error" : ""}`}
              value={form.mes_inicio}
              onChange={(e) => handleChange("mes_inicio", Number(e.target.value))}
            >
              {MONTHS.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </FormField>
          <FormField label="Mes fim" error={errors["mes_fim"]} htmlFor="mes_fim">
            <select
              id="mes_fim"
              className={`input-base ${errors["mes_fim"] ? "input-error" : ""}`}
              value={form.mes_fim}
              onChange={(e) => handleChange("mes_fim", Number(e.target.value))}
            >
              {MONTHS.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </FormField>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={updatePeriodo.isPending}
          >
            {updatePeriodo.isPending ? (
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
