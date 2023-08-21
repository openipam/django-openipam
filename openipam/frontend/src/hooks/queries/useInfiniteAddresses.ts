import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const useInfiniteAddresses = (p: {
  [key: string]: string | boolean | undefined;
}) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["addresses", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.addresses.get({ page: pageParam, ...p });
      return {
        addresses: results.results,
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
    if (
      query.hasNextPage &&
      !query.isFetchingNextPage &&
      (p.getAll || currentPage < 1)
    ) {
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
