import React from "react";
import { useApi } from "../useApi";
import { useQueryBuilder } from "./usePrefetchedQuery";

export const useInfiniteHostDhcpRecords = (p: {
  host?: string | undefined;
  mac?: string | undefined;
  [key: string]: string | undefined;
}) => {
  const api = useApi();
  const query = useQueryBuilder({
    queryKey: ["dhcp, host", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      const results = await api.dns.dhcp({
        ...Object.fromEntries(Object.entries(p).filter(([_, v]) => v)),
        page,
      });
      return {
        dhcp: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
  });
  return query;
};
