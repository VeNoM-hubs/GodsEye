import { useEffect, useState } from "react";
import type { ResourceRow } from "@shared/cyber-api";
import { fetchResources } from "@/lib/api-client";

export function useResources() {
  const [resources, setResources] = useState<ResourceRow[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  useEffect(() => {
    fetchResources()
      .then((data) => { setResources(data); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  return { resources, loading, error };
}
