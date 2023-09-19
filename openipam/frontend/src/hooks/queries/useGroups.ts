import { useInfiniteQuery } from "@tanstack/react-query";
import { useApi } from "../useApi";
import { useEffect } from "react";

export const useGroups = (p: {
  [key: string]: string | boolean | undefined;
}) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["groups", p.name],
    queryFn: async ({ pageParam = 0 }) => {
      const results = await api.groups.get({
        page: pageParam + 1,
        page_size: 100,
        ...p,
      });
      return {
        groups: results.results,
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
