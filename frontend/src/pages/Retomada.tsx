import { useState } from "react";
import { RotateCcw, Loader2, ArrowRight } from "lucide-react";
import { useQuery, useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { progressApi, downloadApi } from "@/api/endpoints";
import { resumeDownloadRequestSchema, type ResumeDownloadFormData } from "@/schemas";
import { FormField } from "@/components/ui/FormField";
import { Badge } from "@/components/ui/Badge";
import type { Checkpoint } from "@/types";

const statusConfig: Record<string, { variant: "success" | "warning" | "error" | "info"; label: string }> = {
  concluido: { variant: "success", label: "Concluido" },
  em_andamento: { variant: "info", label: "Em andamento" },
  erro: { variant: "error", label: "Erro" },
  pendente: { variant: "warning", label: "Pendente" },
};

export function Retomada() {
  const { data, isLoading } = useQuery({
    queryKey: ["checkpoints"],
    queryFn: progressApi.checkpoints,
  });
  const checkpoints = data?.items ?? [];

  const resumeMutation = useMutation({
    mutationFn: downloadApi.resumeFromCheckpoint,
  });

  const [form, setForm] = useState<ResumeDownloadFormData>({
    endpoint_retomada: "despesas",
    ano_retomada: 2024,
    mes_retomada: 1,
    pagina_retomada: 1,
    ignorar_arquivos_existentes: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  function handleChange(field: keyof ResumeDownloadFormData, value: string | number | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function handleUseCheckpoint(cp: Checkpoint) {
    setForm({
      endpoint_retomada: cp.endpoint,
      ano_retomada: cp.ano,
      mes_retomada: cp.mes,
      pagina_retomada: cp.pagina,
      ignorar_arquivos_existentes: false,
    });
    setErrors({});
    toast("Checkpoint carregado no formulario.", { icon: "\u2139\uFE0F" });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = resumeDownloadRequestSchema.safeParse(form);
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
    resumeMutation.mutate(result.data, {
      onSuccess: () => toast.success("Download retomado a partir do checkpoint."),
      onError: () => toast.error("Nao foi possivel retomar o download."),
    });
  }

  return (
    <div>
      <h2 className="text-h2 text-[var(--theme-text)] flex items-center gap-3 mb-6">
        <RotateCcw size={24} /> Retomada de Download
      </h2>
      <p className="text-body text-[var(--theme-text-secondary)] mb-6">
        Retome um download a partir de um checkpoint salvo ou configure manualmente o ponto de partida.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div>
          <h3 className="text-h4 text-[var(--theme-text)] mb-4">Configuracao de Retomada</h3>
          <form onSubmit={handleSubmit} className="card space-y-5">
            <FormField label="Endpoint" required error={errors["endpoint_retomada"]} htmlFor="endpoint_retomada">
              <select
                id="endpoint_retomada"
                className={`input-base ${errors["endpoint_retomada"] ? "input-error" : ""}`}
                value={form.endpoint_retomada}
                onChange={(e) => handleChange("endpoint_retomada", e.target.value)}
              >
                <option value="despesas">Despesas</option>
                <option value="receitas">Receitas</option>
              </select>
            </FormField>

            <div className="grid grid-cols-3 gap-3">
              <FormField label="Ano" required error={errors["ano_retomada"]} htmlFor="ano_retomada">
                <input
                  id="ano_retomada"
                  type="number"
                  min={2004}
                  max={2026}
                  className={`input-base font-mono ${errors["ano_retomada"] ? "input-error" : ""}`}
                  value={form.ano_retomada}
                  onChange={(e) => handleChange("ano_retomada", Number(e.target.value))}
                />
              </FormField>
              <FormField label="Mes" required error={errors["mes_retomada"]} htmlFor="mes_retomada">
                <input
                  id="mes_retomada"
                  type="number"
                  min={1}
                  max={12}
                  className={`input-base font-mono ${errors["mes_retomada"] ? "input-error" : ""}`}
                  value={form.mes_retomada}
                  onChange={(e) => handleChange("mes_retomada", Number(e.target.value))}
                />
              </FormField>
              <FormField label="Pagina" required error={errors["pagina_retomada"]} htmlFor="pagina_retomada">
                <input
                  id="pagina_retomada"
                  type="number"
                  min={1}
                  className={`input-base font-mono ${errors["pagina_retomada"] ? "input-error" : ""}`}
                  value={form.pagina_retomada}
                  onChange={(e) => handleChange("pagina_retomada", Number(e.target.value))}
                />
              </FormField>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                className={`toggle-switch ${form.ignorar_arquivos_existentes ? "active" : ""}`}
                onClick={() => handleChange("ignorar_arquivos_existentes", !form.ignorar_arquivos_existentes)}
                role="switch"
                aria-checked={form.ignorar_arquivos_existentes}
              />
              <span className="text-body text-[var(--theme-text)]">Ignorar arquivos existentes</span>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={resumeMutation.isPending}
            >
              {resumeMutation.isPending ? (
                <><Loader2 size={16} className="animate-spin" /> Retomando...</>
              ) : (
                <><ArrowRight size={16} /> Retomar Download</>
              )}
            </button>
          </form>
        </div>

        {/* Checkpoints table */}
        <div>
          <h3 className="text-h4 text-[var(--theme-text)] mb-4">Checkpoints Salvos</h3>
          <div className="card !p-0 overflow-hidden">
            {isLoading ? (
              <div className="flex items-center justify-center gap-2 p-8 text-[var(--theme-text-secondary)]">
                <Loader2 size={18} className="animate-spin" /> Carregando checkpoints...
              </div>
            ) : checkpoints.length === 0 ? (
              <div className="p-8 text-center text-[var(--theme-text-secondary)]">
                Nenhum checkpoint disponivel para retomada.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr style={{ backgroundColor: "var(--theme-surface-2)" }}>
                      <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Endpoint</th>
                      <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Periodo</th>
                      <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Pagina</th>
                      <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Status</th>
                      <th className="text-left px-4 py-3 text-caption font-medium text-[var(--theme-text-secondary)]">Atualizado</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="table-zebra">
                    {checkpoints.map((cp) => {
                      const st = statusConfig[cp.status] ?? statusConfig.pendente;
                      return (
                        <tr key={cp.id} style={{ borderTop: "1px solid var(--theme-border)" }}>
                          <td className="px-4 py-2 text-[var(--theme-text)] capitalize">{cp.endpoint}</td>
                          <td className="px-4 py-2 font-mono text-xs text-[var(--theme-text)]">
                            {cp.ano}/{String(cp.mes).padStart(2, "0")}
                          </td>
                          <td className="px-4 py-2 font-mono text-xs text-[var(--theme-text)]">{cp.pagina}</td>
                          <td className="px-4 py-2">
                            <Badge variant={st.variant}>{st.label}</Badge>
                          </td>
                          <td className="px-4 py-2 font-mono text-xs text-[var(--theme-text-secondary)] whitespace-nowrap">
                            {cp.last_update}
                          </td>
                          <td className="px-4 py-2">
                            <button
                              className="btn btn-secondary !h-7 !px-3 text-xs"
                              onClick={() => handleUseCheckpoint(cp)}
                            >
                              Usar
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
