import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteMyHosts = (p: {
  show_groups: false;
  [key: string]: string | number | boolean;
}) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: [
      "Hosts, mine",
      ...Object.entries(p).map(([k, v]) => `${k}=${v}`),
    ],
    queryFn: async (page) => {
      const results = await api.hosts.mine({
        ...Object.fromEntries(Object.entries(p).filter(([_, val]) => val)),
        page,
      });
      return {
        results: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
    ...p,
  });
  return query;
};
