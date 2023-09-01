import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const usePrefetchedInfiniteHosts = (p: {
  page: number;
  [key: string]: string | number;
}) => {
  const data = useInfiniteHosts(p);
  useInfiniteHosts({
    ...p,
    page: p.page + 1,
  });
  return data;
};

export const useInfiniteHosts = (p: {
  page: number;
  [key: string]: string | number;
}) => {
  const api = useApi();

  const query = useInfiniteQuery({
    queryKey: [
      "Hosts, all",
      ...Object.entries(p)
        .filter(([key, _]) => key !== "selectAll" && key !== "page_size")
        .flat(),
    ],
    queryFn: async () => {
      let results;
      try {
        if (p.disabled === "N") {
          results = await api.hosts.disabled({
            page: p.page,
            ...Object.fromEntries(
              Object.entries(p).filter(
                ([key, val]) => val && key !== "page_size"
              )
            ),
          });
        } else {
          results = await api.hosts.get({
            page: p.page,
            ...Object.fromEntries(
              Object.entries(p).filter(
                ([key, val]) => val && key !== "page_size"
              )
            ),
            disabled: !!p.disabled,
          });
        }
        return {
          results: results.results,
          count: results.count,
          page: p.page,
          nextPage: results.next,
        };
      } catch (e) {
        console.error(e);
        return {
          results: [],
          count: 0,
          page: p.page,
          nextPage: false,
        };
      }
    },
    getNextPageParam: (lastPage) => {
      return lastPage.nextPage ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 1;
    if (
      query.hasNextPage &&
      !query.isFetchingNextPage &&
      (p.selectAll ||
        (query.data?.pages?.length ?? 0) <
          ((p.page_size ?? 10) as number) / 10 ||
        currentPage < 1)
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
