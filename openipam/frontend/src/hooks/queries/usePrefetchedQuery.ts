import { useInfiniteQuery } from "@tanstack/react-query";
import React, { useEffect } from "react";

export const usePrefetchedQuery = (p: {
  queryKey: string[];
  queryFn: (page?: any) => Promise<any>;
  [key: string]: any;
}) => {
  const query = useQueryBuilder(p);

  // Prefetch the next page
  useQueryBuilder({
    ...p,
    queryKey: p.queryKey.map((x) => {
      if (x.startsWith("page=")) {
        return `page=${(p.page ?? 1) + 1}`;
      }
      return x;
    }),
    page: (p.page ?? 1) + 1,
  });

  return query;
};

export const useQueryBuilder = (p: {
  queryKey: string[];
  queryFn: (page?: any) => Promise<any>;
  [key: string]: any;
}) => {
  const query = useInfiniteQuery({
    queryFn: () => p.queryFn(p.page ?? 1),
    queryKey: p.queryKey,
    getNextPageParam: (lastPage) => {
      return lastPage.nextPage ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 1;
    if (
      query.hasNextPage &&
      !query.isFetchingNextPage &&
      (p.selectAll || currentPage < 1)
    ) {
      query.fetchNextPage();
    }
  }, [
    query.hasNextPage,
    query.isFetchingNextPage,
    query.fetchNextPage,
    query.data,
    p.selectAll,
    p.page_size,
  ]);
  return query;
};
