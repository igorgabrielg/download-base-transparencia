import { useMutation } from "@tanstack/react-query";

import { downloadApi } from "@/api/endpoints";

export function useDownload() {
  const start = useMutation({ mutationFn: downloadApi.start });
  const pause = useMutation({ mutationFn: downloadApi.pause });
  const resume = useMutation({ mutationFn: downloadApi.resume });
  const stop = useMutation({ mutationFn: downloadApi.stop });

  return { start, pause, resume, stop };
}
