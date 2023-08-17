import { useInfiniteQuery } from "@tanstack/react-query";
import { useApi } from "../useApi";
import { useEffect } from "react";
import { get } from "http";

export const useDhcpGroups = () => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["dhcpGroups"],
    queryFn: async ({ pageParam = 0 }) => {
      const results = await api.dhcpGroups.get({ page: pageParam + 1 });
      return {
        dhcpGroups: results.results,
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
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 15) {
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
