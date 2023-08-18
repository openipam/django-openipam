import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const useInfiniteHosts = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["Hosts, all", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      let results;
      if (p.disabled === "N") {
        results = await api.hosts.disabled({
          page: pageParam,
          ...Object.fromEntries(Object.entries(p).filter(([_, val]) => val)),
        });
      } else {
        results = await api.hosts.get({
          page: pageParam,
          ...Object.fromEntries(Object.entries(p).filter(([_, val]) => val)),
          disabled: !!p.disabled,
        });
      }
      return {
        results: results.results,
        page: pageParam,
        nextPage: results.next,
      };
    },
    getNextPageParam: (lastPage) => {
      return lastPage.nextPage ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 0;
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 1) {
      query.fetchNextPage();
    }
  }, [
    query.hasNextPage,
    query.isFetchingNextPage,
    query.fetchNextPage,
    query.data,
  ]);
  return query;
};
