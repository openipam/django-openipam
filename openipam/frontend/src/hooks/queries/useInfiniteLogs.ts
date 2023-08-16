import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const useInfiniteLogs = (p: { [key: string]: string }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["logs", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      if (p.type === "email") {
        const results = await api.logs.getEmails({ page: pageParam, ...p });
        return {
          emails: results.results,
          page: pageParam,
          nextPage: results.next,
        };
      }
      const results = await api.logs.get({ page: pageParam, ...p });
      return {
        logs: results.results,
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
