import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const useInfiniteHosts = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: [
      "Hosts, all",
      ...Object.entries(p)
        .filter(([key, _]) => key !== "selectAll" && key !== "page_size")
        .flat(),
    ],
    queryFn: async ({ pageParam = 1 }) => {
      let results;
      try {
        if (p.disabled === "N") {
          results = await api.hosts.disabled({
            page: pageParam,
            ...Object.fromEntries(
              Object.entries(p).filter(
                ([key, val]) => val && key !== "page_size"
              )
            ),
          });
        } else {
          results = await api.hosts.get({
            page: pageParam,
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
          page: pageParam,
          nextPage: results.next,
        };
      } catch (e) {
        console.error(e);
        return {
          results: [],
          count: 0,
          page: pageParam,
          nextPage: false,
        };
      }
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
      (p.selectAll ||
        (query.data?.pages?.length ?? 0) <
          ((p.page_size ?? 10) as number) / 10 ||
        currentPage < 4)
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
