import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteDomains = (p: {
  [key: string]: string | number;
  page: number;
}) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: [
      "domains, all",
      ...Object.entries(p).map(([k, v]) => `${k}=${v}`),
    ],
    queryFn: async (page) => {
      const results = await api.domains.get({
        ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
        page,
      });
      return {
        results: results.results,
        page,
        count: results.count,
        nextPage: results.next,
      };
    },
    ...p,
  });
  return query;
};
