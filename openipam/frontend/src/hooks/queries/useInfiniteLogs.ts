import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteLogs = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = usePrefetchedQuery({
    queryKey: ["logs", ...Object.entries(p).map(([k, v]) => `${k}=${v}`)],
    queryFn: async (page) => {
      try {
        if (p.type === "email") {
          const results = await api.logs.getEmails({
            ...Object.fromEntries(
              Object.entries(p).filter(([key, val]) => val)
            ),
            page,
          });
          return {
            emails: results.results,
            page,
            nextPage: results.next,
            count: results.count,
          };
        }
        const results = await api.logs.get({
          ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
          page,
        });
        return {
          logs: results.results,
          page,
          nextPage: results.next,
          count: results.count,
        };
      } catch (e) {
        console.log(e);
        return {
          logs: [],
          page: 0,
          nextPage: 0,
          count: 0,
        };
      }
    },
    ...p,
  });
  return query;
};
