import React from "react";
import { useApi } from "../useApi";
import { useQueryBuilder } from "./usePrefetchedQuery";

export const useInfiniteAddresses = (p: {
  [key: string]: string | boolean | number | undefined;
}) => {
  const api = useApi();
  const query = useQueryBuilder({
    queryKey: ["addresses", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      const results = await api.addresses.get({ ...p, page });
      return {
        addresses: results.results,
        page,
        nextPage: results.next,
      };
    },
  });
  return query;
};
