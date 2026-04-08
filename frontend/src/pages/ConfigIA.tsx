import { useState, useEffect } from "react";
import { Cpu, Loader2, Sparkles } from "lucide-react";
import toast from "react-hot-toast";

import { useConfig, useUpdateIA } from "@/hooks/useConfig";
import { configIARequestSchema, type ConfigIAFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";

export function ConfigIA() {
  const { data: config, isLoading } = useConfig();
  const updateIA = useUpdateIA();

  const [form, setForm] = useState<ConfigIAFormData>({
    gemini_api_key: "",
    anthropic_api_key: "",
    ia_provider: "gemini",
    ia_model: "gemini-3.5-flash",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setForm({
        gemini_api_key: config.gemini_api_key || "",
        anthropic_api_key: config.anthropic_api_key || "",
        ia_provider: config.ia_provider || "gemini",
        ia_model: config.ia_model || "gemini-3.5-flash",
      });
    }
  }, [config]);

  // Atualiza dinamicamente o modelo padrão se o provedor mudar e o modelo for o padrão do anterior
  function handleProviderChange(provider: "gemini" | "claude") {
    setForm((prev) => {
      let nextModel = prev.ia_model;
      if (provider === "gemini" && (prev.ia_model.startsWith("claude") || prev.ia_model === "")) {
        nextModel = "gemini-3.5-flash";
      } else if (provider === "claude" && (prev.ia_model.startsWith("gemini") || prev.ia_model === "")) {
        nextModel = "claude-3-5-sonnet-20241022";
      }
      return {
        ...prev,
        ia_provider: provider,
        ia_model: nextModel,
      };
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = configIARequestSchema.safeParse(form);
    
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
    updateIA.mutate(result.data, {
      onSuccess: () => toast.success("Configurações de IA salvas com sucesso."),
      onError: () => toast.error("Não foi possível salvar as configurações de IA."),
    });
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-[var(--theme-text-secondary)]">
        <Loader2 size={18} className="animate-spin" /> Carregando configuração...
      </div>
    );
  }

  return (
    <div className="page-config">
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <Cpu size={24} /> Configuração de Inteligência Artificial
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Defina as chaves de acesso (API Keys), provedor padrão e os modelos cognitivos para auditoria inteligente dos dados.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <h3 className="text-h4 text-[var(--theme-text)] mb-3">Provedor Ativo</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => handleProviderChange("gemini")}
              className={`p-4 rounded-lg border text-left transition-all flex flex-col justify-between ${
                form.ia_provider === "gemini"
                  ? "border-[var(--theme-accent)] bg-[var(--theme-accent)]/5 text-[var(--theme-text)] font-semibold shadow-sm"
                  : "border-[var(--theme-border)] hover:border-[var(--theme-text-secondary)] text-[var(--theme-text-secondary)]"
              }`}
            >
              <div className="flex items-center gap-2">
                <Sparkles size={18} className="text-[var(--theme-accent)]" />
                <span>Google Gemini (via CLI agy)</span>
              </div>
              <span className="text-[11px] font-normal mt-2 opacity-80">
                Processamento local direto via CLI agy. Ideal para análises volumosas sem API keys.
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleProviderChange("claude")}
              className={`p-4 rounded-lg border text-left transition-all flex flex-col justify-between ${
                form.ia_provider === "claude"
                  ? "border-[var(--theme-accent)] bg-[var(--theme-accent)]/5 text-[var(--theme-text)] font-semibold shadow-sm"
                  : "border-[var(--theme-border)] hover:border-[var(--theme-text-secondary)] text-[var(--theme-text-secondary)]"
              }`}
            >
              <div className="flex items-center gap-2">
                <Cpu size={18} className="text-[var(--theme-warning)]" />
                <span>Anthropic Claude</span>
              </div>
              <span className="text-[11px] font-normal mt-2 opacity-80">
                Pareceres textuais extremamente detalhados e críticos com foco em auditoria.
              </span>
            </button>
          </div>
        </div>

        <h3 className="text-h4 text-[var(--theme-text)] border-t border-[var(--theme-border)] pt-4">Credenciais</h3>

        {form.ia_provider === "gemini" ? (
          <div className="p-4 rounded-lg border border-[var(--theme-accent)]/30 bg-[var(--theme-accent)]/5 text-[var(--theme-text)] text-sm space-y-2">
            <div className="flex items-center gap-2 font-semibold text-[var(--theme-accent)]">
              <Sparkles size={16} />
              <span>Autonomia de IA via Antigravity CLI (agy)</span>
            </div>
            <p className="text-xs text-[var(--theme-text-secondary)] leading-relaxed">
              O provedor <strong>Google Gemini</strong> está configurado para operar diretamente por meio da CLI local <code>agy</code> instalada no seu ambiente de execução. Nenhuma chave de API precisa ser informada nesta tela.
            </p>
          </div>
        ) : (
          <FormField
            label="Anthropic Claude API Key"
            error={errors["anthropic_api_key"]}
            htmlFor="anthropic_api_key"
            hint="Se deixada em branco, tentará ler o fallback ANTHROPIC_API_KEY ou CLAUDE_API_KEY do ambiente do servidor."
          >
            <input
              id="anthropic_api_key"
              type="password"
              className={`input-base font-mono ${errors["anthropic_api_key"] ? "input-error" : ""}`}
              placeholder="sk-ant-..."
              value={form.anthropic_api_key}
              onChange={(e) => {
                setForm((prev) => ({ ...prev, anthropic_api_key: e.target.value }));
                setErrors((prev) => { const n = { ...prev }; delete n["anthropic_api_key"]; return n; });
              }}
            />
          </FormField>
        )}

        <h3 className="text-h4 text-[var(--theme-text)] border-t border-[var(--theme-border)] pt-4">Modelo do Agente</h3>

        <FormField
          label="Nome do Modelo"
          required
          error={errors["ia_model"]}
          htmlFor="ia_model"
          hint="Certifique-se de preencher um identificador oficial válido."
        >
          <div className="relative">
            <input
              id="ia_model"
              type="text"
              className={`input-base font-mono ${errors["ia_model"] ? "input-error" : ""}`}
              placeholder={form.ia_provider === "gemini" ? "gemini-3.5-flash" : "claude-3-5-sonnet-20241022"}
              value={form.ia_model}
              onChange={(e) => {
                setForm((prev) => ({ ...prev, ia_model: e.target.value }));
                setErrors((prev) => { const n = { ...prev }; delete n["ia_model"]; return n; });
              }}
            />
            
            <div className="flex gap-2 mt-2">
              <span className="text-[10px] text-[var(--theme-text-secondary)]">Sugestões comuns:</span>
              {form.ia_provider === "gemini" ? (
                <>
                  <button
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, ia_model: "gemini-3.5-flash" }))}
                    className="text-[10px] text-[var(--theme-accent)] hover:underline"
                  >
                    gemini-3.5-flash
                  </button>
                  <span className="text-[10px] text-[var(--theme-border)]">|</span>
                  <button
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, ia_model: "gemini-1.5-flash" }))}
                    className="text-[10px] text-[var(--theme-accent)] hover:underline"
                  >
                    gemini-1.5-flash
                  </button>
                  <span className="text-[10px] text-[var(--theme-border)]">|</span>
                  <button
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, ia_model: "gemini-1.5-pro" }))}
                    className="text-[10px] text-[var(--theme-accent)] hover:underline"
                  >
                    gemini-1.5-pro
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, ia_model: "claude-3-5-sonnet-20241022" }))}
                    className="text-[10px] text-[var(--theme-accent)] hover:underline"
                  >
                    claude-3.5-sonnet
                  </button>
                  <span className="text-[10px] text-[var(--theme-border)]">|</span>
                  <button
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, ia_model: "claude-3-5-haiku-20241022" }))}
                    className="text-[10px] text-[var(--theme-accent)] hover:underline"
                  >
                    claude-3.5-haiku
                  </button>
                </>
              )}
            </div>
          </div>
        </FormField>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            className="btn btn-primary animate-hover-button"
            disabled={updateIA.isPending}
          >
            {updateIA.isPending ? (
              <><Loader2 size={16} className="animate-spin" /> Salvando...</>
            ) : (
              "Salvar Configuração"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
