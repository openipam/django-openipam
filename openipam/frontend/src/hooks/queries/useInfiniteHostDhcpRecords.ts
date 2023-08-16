import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const useInfiniteHostDhcpRecords = (p: {
  host?: string | undefined;
  mac?: string | undefined;
  [key: string]: string | undefined;
}) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["dhcp, host", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.dns.dhcp({
        page: pageParam,
        ...Object.fromEntries(Object.entries(p).filter(([_, v]) => v)),
      });
      return {
        dhcp: results.results,
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
