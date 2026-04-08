import { useQuery } from "@tanstack/react-query";

import { logsApi } from "@/api/endpoints";
import type { LogFilters } from "@/types";

export function useLogs(filters?: LogFilters) {
  return useQuery({
    queryKey: ["logs", filters],
    queryFn: () => logsApi.list(filters),
    refetchInterval: 5000,
  });
}
