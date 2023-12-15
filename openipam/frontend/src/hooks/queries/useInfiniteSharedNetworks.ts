import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteSharedNetworks = (p: {
  [key: string]: string | boolean | number | undefined;
}) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: [
      "sharedNetworks",
      ...Object.entries(p).map(([k, v]) => `${k}=${v}`),
    ],
    queryFn: async (page) => {
      const results = await api.networks.getSharedNetworks({
        ...Object.fromEntries(Object.entries(p).filter(([_, val]) => val)),
        page,
      });
      return {
        networks: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
    ...p,
  });
  return query;
};
