import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteNetworkAddresses = (p: {
  network: string;
  range: string;
  [key: string]: string | number | undefined;
}) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: [
      "network, Addresses",
      ...Object.entries(p).map(([k, v]) => `${k}=${v}`),
    ],
    queryFn: async (page) => {
      const results = await api.networks
        .byId(`${p.network}/${p.range}`)
        .addresses.get({
          ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
          page,
        });
      return {
        addresses: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
    ...p,
  });
  return query;
};
