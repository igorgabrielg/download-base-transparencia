import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { configApi } from "@/api/endpoints";
import type {
  ConfigTokensRequest,
  ConfigPeriodoRequest,
  ConfigRateLimitRequest,
  ConfigEndpointsRequest,
  ConfigSaidaRequest,
  ConfigIARequest,
} from "@/types";
import { iaApi } from "@/api/endpoints";

export function useConfig() {
  return useQuery({ queryKey: ["config"], queryFn: configApi.get });
}

export function useUpdateTokens() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfigTokensRequest) => configApi.updateTokens(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });
}

export function useUpdatePeriodo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfigPeriodoRequest) => configApi.updatePeriodo(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });
}

export function useUpdateRateLimit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfigRateLimitRequest) => configApi.updateRateLimit(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });
}

export function useUpdateEndpoints() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfigEndpointsRequest) => configApi.updateEndpoints(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });
}

export function useUpdateSaida() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfigSaidaRequest) => configApi.updateSaida(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });
}

export function useValidateTokens() {
  return useMutation({ mutationFn: configApi.validateTokens });
}

export function useUpdateIA() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfigIARequest) => configApi.updateIA(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });
}

export function useAnalyzeIA() {
  return useMutation({
    mutationFn: () => iaApi.analyze(),
  });
}

export function useSynthesizeIA() {
  return useMutation({
    mutationFn: () => iaApi.synthesize(),
  });
}

export function useIndexIA() {
  return useMutation({
    mutationFn: () => iaApi.index(),
  });
}

export function useChatIA() {
  return useMutation({
    mutationFn: (pergunta: string) => iaApi.chat(pergunta),
  });
}

export function usePipelineCompletoIA() {
  return useMutation({
    mutationFn: () => iaApi.runPipelineCompleto(),
  });
}



