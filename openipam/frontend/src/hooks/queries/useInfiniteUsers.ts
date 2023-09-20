import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteUsers = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: ["users, all", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      const results = await api.user.get({
        ...Object.fromEntries(
          Object.entries(p).filter(
            ([key, val]) => val !== undefined && val !== null
          )
        ),
        page,
      });
      return {
        users: results.results,
        page,
        nextPage: results.next,
        count: results.count,
      };
    },
    ...p,
  });
  return query;
};
