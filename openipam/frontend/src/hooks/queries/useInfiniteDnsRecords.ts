import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteDnsRecords = (p: {
  domain: string;
  [key: string]: string | number;
}) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: ["domain", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      const results = await api.domains.byId(p.domain).dns.get({
        ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
        page,
      });
      return {
        dns: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
    ...p,
  });
  return query;
};
