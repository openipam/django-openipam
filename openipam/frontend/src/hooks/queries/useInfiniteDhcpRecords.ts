import React from "react";
import { useApi } from "../useApi";
import { useQueryBuilder } from "./usePrefetchedQuery";

export const useInfiniteDhcpRecords = (p: {
  domain: string;
  [key: string]: string | number;
}) => {
  const api = useApi();
  const query = useQueryBuilder({
    queryKey: ["dhcp", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      const results = await api.domains.byId(p.domain).dhcp.get({
        ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
        page,
      });
      return {
        dhcp: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
    ...p,
  });
  return query;
};
