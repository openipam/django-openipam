import React from "react";
import { useApi } from "../useApi";
import { useQueryBuilder } from "./usePrefetchedQuery";

export const useInfiniteHostDnsRecords = (p: {
  host?: string | undefined;
  mac?: string | undefined;
  [key: string]: string | undefined;
}) => {
  const api = useApi();
  const query = useQueryBuilder({
    queryKey: ["host, dns", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      const results = await api.dns.get({ ...p, page });
      return {
        dns: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
  });
  return query;
};
