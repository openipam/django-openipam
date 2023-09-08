import React from "react";
import { useApi } from "../useApi";
import { usePrefetchedQuery } from "./usePrefetchedQuery";

export const useInfiniteHosts = (p: {
  page: number;
  quickFilter: string[][] | undefined;
  [key: string]: string | number | string[][] | undefined;
}) => {
  const quickFilter = Object.fromEntries(p.quickFilter ?? []) ?? {};
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
      if (quickFilter.mine || quickFilter.show_groups) {
        results = await api.hosts.mine({
          ...Object.fromEntries(
            Object.entries(p).filter(
              ([key, val]) => val && key !== "quickFilter"
            )
          ),
          page,
          ...quickFilter,
        });
      } else if (p.disabled === "N") {
        results = await api.hosts.disabled({
          ...Object.fromEntries(
            Object.entries(p).filter(
              ([key, val]) => val && key !== "quickFilter"
            )
          ),
          page,
          ...quickFilter,
        });
      } else {
        results = await api.hosts.get({
          ...Object.fromEntries(
            Object.entries(p).filter(
              ([key, val]) => val && key !== "quickFilter"
            )
          ),
          disabled: !!p.disabled,
          page,
          ...quickFilter,
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
