import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteHosts = (p: {
  page: number;
  [key: string]: string | number;
}) => {
  const api = useApi();
  const queryKey = [
    "Hosts, all",
    ...Object.entries(p)
      .filter(([key, _]) => key !== "selectAll")
      .map(([key, val]) => `${key}=${val}`),
  ];
  const queryFn = async (page: string | number) => {
    let results;
    try {
      if (p.disabled === "N") {
        results = await api.hosts.disabled({
          ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
          page,
        });
      } else {
        results = await api.hosts.get({
          ...Object.fromEntries(Object.entries(p).filter(([key, val]) => val)),
          disabled: !!p.disabled,
          page,
        });
      }
      return {
        results: results.results,
        count: results.count,
        page,
        nextPage: results.next,
      };
    } catch (e) {
      console.error(e);
      return {
        results: [],
        count: 0,
        page,
        nextPage: false,
      };
    }
  };

  const query = usePrefetchedQuery({
    ...p,
    queryKey,
    queryFn,
  });

  return query;
};
