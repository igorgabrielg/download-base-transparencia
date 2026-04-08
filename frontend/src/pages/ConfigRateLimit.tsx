import { useState, useEffect } from "react";
import { Gauge, Loader2, RotateCcw } from "lucide-react";
import toast from "react-hot-toast";

import { useConfig, useUpdateRateLimit } from "@/hooks/useConfig";
import { configRateLimitRequestSchema, type ConfigRateLimitFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";

const DEFAULTS: ConfigRateLimitFormData = {
  max_req_madrugada: 590,
  max_req_dia: 390,
  max_req_restrita: 170,
  velocidade_req_min: 60,
  fuso_horario: "America/Sao_Paulo",
  tamanho_pagina: 500,
};

export function ConfigRateLimit() {
  const { data: config, isLoading } = useConfig();
  const updateRateLimit = useUpdateRateLimit();

  const [form, setForm] = useState<ConfigRateLimitFormData>(DEFAULTS);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setForm({
        max_req_madrugada: config.max_req_madrugada,
        max_req_dia: config.max_req_dia,
        max_req_restrita: config.max_req_restrita,
        velocidade_req_min: config.velocidade_req_min,
        fuso_horario: config.fuso_horario,
        tamanho_pagina: config.tamanho_pagina,
      });
    }
  }, [config]);

  function handleChange(field: keyof ConfigRateLimitFormData, value: number | string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = configRateLimitRequestSchema.safeParse(form);
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
    updateRateLimit.mutate(result.data, {
      onSuccess: () => toast.success("Rate limit salvo com sucesso."),
      onError: () => toast.error("Nao foi possivel salvar o rate limit."),
    });
  }

  function handleRestore() {
    setForm(DEFAULTS);
    setErrors({});
    toast("Valores restaurados para padrao.", { icon: "\u2139\uFE0F" });
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
        <Gauge size={24} /> Configuracao de Rate Limit
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Ajuste os limites de requisicoes por minuto para cada faixa horaria.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <h3 className="text-h4 text-[var(--theme-text)]">Limites por Faixa Horaria</h3>

        <FormField
          label="Madrugada (00h-06h)"
          required
          error={errors["max_req_madrugada"]}
          htmlFor="max_req_madrugada"
          hint="Requisicoes permitidas por minuto entre 00h e 06h (horario de Brasilia)."
        >
          <input
            id="max_req_madrugada"
            type="number"
            min={1}
            max={700}
            className={`input-base font-mono ${errors["max_req_madrugada"] ? "input-error" : ""}`}
            value={form.max_req_madrugada}
            onChange={(e) => handleChange("max_req_madrugada", Number(e.target.value))}
          />
        </FormField>

        <FormField
          label="Dia (06h-24h)"
          required
          error={errors["max_req_dia"]}
          htmlFor="max_req_dia"
          hint="Requisicoes permitidas por minuto entre 06h e 24h."
        >
          <input
            id="max_req_dia"
            type="number"
            min={1}
            max={400}
            className={`input-base font-mono ${errors["max_req_dia"] ? "input-error" : ""}`}
            value={form.max_req_dia}
            onChange={(e) => handleChange("max_req_dia", Number(e.target.value))}
          />
        </FormField>

        <FormField
          label="Faixa restrita"
          required
          error={errors["max_req_restrita"]}
          htmlFor="max_req_restrita"
          hint="Limite mais conservador para horarios de alta demanda."
        >
          <input
            id="max_req_restrita"
            type="number"
            min={1}
            max={180}
            className={`input-base font-mono ${errors["max_req_restrita"] ? "input-error" : ""}`}
            value={form.max_req_restrita}
            onChange={(e) => handleChange("max_req_restrita", Number(e.target.value))}
          />
        </FormField>

        <h3 className="text-h4 text-[var(--theme-text)]">Velocidade de Requisicao</h3>

        <FormField
          label="Velocidade (req/min)"
          required
          error={errors["velocidade_req_min"]}
          htmlFor="velocidade_req_min"
          hint="Controla a velocidade das requisicoes. Ex: 60 = 1 req/seg, 120 = 2 req/seg. O sistema nunca ultrapassa o limite do periodo (dia/noite)."
        >
          <input
            id="velocidade_req_min"
            type="number"
            min={1}
            max={600}
            className={`input-base font-mono ${errors["velocidade_req_min"] ? "input-error" : ""}`}
            value={form.velocidade_req_min}
            onChange={(e) => handleChange("velocidade_req_min", Number(e.target.value))}
          />
          <span className="text-caption text-[var(--theme-text-secondary)] mt-1 block">
            {form.velocidade_req_min > 0
              ? `~${(60 / form.velocidade_req_min).toFixed(2)}s entre cada requisicao`
              : ""}
          </span>
        </FormField>

        <h3 className="text-h4 text-[var(--theme-text)]">Paginacao e Fuso</h3>

        <FormField
          label="Tamanho de pagina"
          required
          error={errors["tamanho_pagina"]}
          htmlFor="tamanho_pagina"
          hint="Quantidade de registros por pagina da API (1-500)."
        >
          <input
            id="tamanho_pagina"
            type="number"
            min={1}
            max={500}
            className={`input-base font-mono ${errors["tamanho_pagina"] ? "input-error" : ""}`}
            value={form.tamanho_pagina}
            onChange={(e) => handleChange("tamanho_pagina", Number(e.target.value))}
          />
        </FormField>

        <FormField
          label="Fuso horario"
          required
          error={errors["fuso_horario"]}
          htmlFor="fuso_horario"
        >
          <input
            id="fuso_horario"
            type="text"
            className={`input-base font-mono ${errors["fuso_horario"] ? "input-error" : ""}`}
            value={form.fuso_horario}
            onChange={(e) => handleChange("fuso_horario", e.target.value)}
          />
        </FormField>

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" className="btn btn-secondary" onClick={handleRestore}>
            <RotateCcw size={16} /> Restaurar Padroes
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={updateRateLimit.isPending}
          >
            {updateRateLimit.isPending ? (
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
