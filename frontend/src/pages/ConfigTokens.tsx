import { useState, useEffect } from "react";
import { Key, CheckCircle, XCircle, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

import { useConfig, useUpdateTokens, useValidateTokens } from "@/hooks/useConfig";
import { configTokensRequestSchema, type ConfigTokensFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";
import { Badge } from "@/components/ui/Badge";
import type { TokenValidationResult } from "@/types";

export function ConfigTokens() {
  const { data: config, isLoading } = useConfig();
  const updateTokens = useUpdateTokens();
  const validateTokens = useValidateTokens();

  const [form, setForm] = useState<ConfigTokensFormData>({
    token_1: "",
    token_2: "",
    token_3: "",
    validar_tokens: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validationResults, setValidationResults] = useState<TokenValidationResult[]>([]);

  useEffect(() => {
    if (config) {
      setForm((prev) => ({
        ...prev,
        token_1: config.token_1 || prev.token_1,
        token_2: config.token_2 || prev.token_2,
        token_3: config.token_3 || prev.token_3,
      }));
    }
  }, [config]);

  function handleChange(field: keyof ConfigTokensFormData, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = configTokensRequestSchema.safeParse(form);
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
    updateTokens.mutate(result.data, {
      onSuccess: () => toast.success("Configuracao de tokens salva com sucesso."),
      onError: () => toast.error("Nao foi possivel salvar os tokens. Tente novamente."),
    });
  }

  function handleValidate() {
    validateTokens.mutate(undefined, {
      onSuccess: (data) => {
        setValidationResults(data);
        const allValid = data.every((r) => r.status === "valido");
        if (allValid) {
          toast.success("Todos os tokens sao validos.");
        } else {
          toast.error("Um ou mais tokens sao invalidos.");
        }
      },
      onError: () => toast.error("Nao foi possivel validar os tokens. Verifique a conexao."),
    });
  }

  function validationBadge(tokenId: string) {
    const result = validationResults.find((r) => r.token_id === tokenId);
    if (!result) return null;
    if (result.status === "valido") {
      return (
        <Badge variant="success">
          <CheckCircle size={12} className="mr-1" /> Valido
        </Badge>
      );
    }
    return (
      <Badge variant="error">
        <XCircle size={12} className="mr-1" /> Invalido
      </Badge>
    );
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
        <Key size={24} /> Configuracao de Tokens
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Informe os tokens de acesso da API do Portal da Transparencia. O Token 1 e obrigatorio.
      </p>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <FormField
          label="Token 1"
          required
          error={errors["token_1"]}
          htmlFor="token_1"
          hint={config?.token_1_set ? "Token ja configurado. Preencha para substituir." : undefined}
        >
          <div className="flex items-center gap-2">
            <input
              id="token_1"
              type="text"
              className={`input-base font-mono ${errors["token_1"] ? "input-error" : ""}`}
              placeholder="Cole o token aqui"
              value={form.token_1}
              onChange={(e) => handleChange("token_1", e.target.value)}
            />
            {validationBadge("token_1")}
          </div>
        </FormField>

        <FormField
          label="Token 2"
          error={errors["token_2"]}
          htmlFor="token_2"
          hint="Opcional. Permite rotacao entre tokens."
        >
          <div className="flex items-center gap-2">
            <input
              id="token_2"
              type="text"
              className={`input-base font-mono ${errors["token_2"] ? "input-error" : ""}`}
              placeholder="Cole o token aqui"
              value={form.token_2}
              onChange={(e) => handleChange("token_2", e.target.value)}
            />
            {validationBadge("token_2")}
          </div>
        </FormField>

        <FormField
          label="Token 3"
          error={errors["token_3"]}
          htmlFor="token_3"
          hint="Opcional. Melhora a taxa de download em horarios de pico."
        >
          <div className="flex items-center gap-2">
            <input
              id="token_3"
              type="text"
              className={`input-base font-mono ${errors["token_3"] ? "input-error" : ""}`}
              placeholder="Cole o token aqui"
              value={form.token_3}
              onChange={(e) => handleChange("token_3", e.target.value)}
            />
            {validationBadge("token_3")}
          </div>
        </FormField>

        <div className="flex items-center gap-3">
          <button
            type="button"
            className={`toggle-switch ${form.validar_tokens ? "active" : ""}`}
            onClick={() => handleChange("validar_tokens", !form.validar_tokens)}
            role="switch"
            aria-checked={form.validar_tokens}
          />
          <span className="text-body text-[var(--theme-text)]">Validar tokens ao salvar</span>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={updateTokens.isPending}
          >
            {updateTokens.isPending ? (
              <><Loader2 size={16} className="animate-spin" /> Salvando...</>
            ) : (
              "Salvar Configuracao"
            )}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleValidate}
            disabled={validateTokens.isPending}
          >
            {validateTokens.isPending ? (
              <><Loader2 size={16} className="animate-spin" /> Validando...</>
            ) : (
              "Validar Tokens"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
