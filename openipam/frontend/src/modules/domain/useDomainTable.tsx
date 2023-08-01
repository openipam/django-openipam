import {
  ColumnFiltersState,
  createColumnHelper,
  getCoreRowModel,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import { useApi } from "../../hooks/useApi";
import {
  betweenDatesFilter,
  fuzzyFilter,
  stringFilter,
} from "../../components/filters";
import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import {
  Add,
  Edit,
  ExpandMore,
  MoreVert,
  Visibility,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

//TODO search permissions, add, edit

type DnsRecord = {
  id: number;
  content: string;
  host: string;
  name: string;
  ttl: number;
  url: string;
  dns_type: string;
};

export const useInfiniteDomain = (p: { domain: string }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["domain", p.domain],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.domains
        .byId(p.domain)
        .dns.get({ page: pageParam });
      console.log("got", results);
      return {
        dns: results.results,
        page: pageParam,
      };
    },
    getNextPageParam: (lastPage) => {
      return lastPage.dns.length > 0 ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 0;
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 10) {
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

export const useDomainTable = (p: { domain: string }) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<DnsRecord[]>([]);
  const navigate = useNavigate();

  const data = useInfiniteDomain(p);
  const dns = useMemo<DnsRecord[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.dns);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.dns)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<DnsRecord>();
  const columns = [
    {
      size: 100,
      enableHiding: false,
      enableSorting: false,
      enableColumnFilter: false,
      id: "actions",
      header: ({ table }: any) => (
        <div className="flex gap-1 items-center relative">
          {/* <PlainIndeterminateCheckbox
                checked={table.getIsAllRowsSelected()}
                indeterminate={table.getIsSomeRowsSelected()}
                onChange={table.getToggleAllRowsSelectedHandler()}
              /> */}
          <div className="tooltip tooltip-right" data-tip="Load More">
            <button
              className="btn btn-circle btn-ghost btn-xs mt-1"
              onClick={() => data.fetchNextPage?.()}
              disabled={!data.hasNextPage || data.isFetchingNextPage}
            >
              <ExpandMore />
            </button>
          </div>
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              alert("TODO: create domain");
            }}
          >
            <Add />
          </button>
        </div>
      ),
      cell: ({ row }: { row: any }) => (
        <div className="flex gap-1 items-center">
          {/* <PlainIndeterminateCheckbox
                checked={row.getIsSelected()}
                onChange={row.getToggleSelectedHandler()}
                disabled={!row.getCanSelect()}
                indeterminate={row.getIsSomeSelected()}
              /> */}
          {/* <button
            className="btn btn-circle btn-ghost btn-xs"
            // onClick={() => navigate(`/domain/${row.original.name}`)}
            disabled={!row.original.name}
          >
            <Visibility fontSize="small" />
          </button> */}
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              alert("TODO: edit domain");
            }}
          >
            <Edit fontSize="small" />
          </button>
        </div>
      ),
    },
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "name",
          header: "Name",
          accessorFn: (row) => row.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "content",
          header: "Content",
          accessorFn: (row) => row.content,
          meta: {
            filterType: "string",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "type",
          header: "Type",
          accessorFn: (row) => row.dns_type,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "ttl",
          header: "Ttl",
          accessorFn: (row) => row.ttl,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "host",
          header: "Host",
          accessorFn: (row) => row.host,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "url",
          header: "URL",
          accessorFn: (row) => row.url,
          meta: {
            filterType: "string",
          },
        },
      ],
    }),
  ];

  const table = useReactTable({
    getCoreRowModel: getCoreRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    // Sorting
    getSortedRowModel: getSortedRowModel(),
    // Filters
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: fuzzyFilter,
    onColumnVisibilityChange: setColumnVisibility,
    data: dns,
    state: {
      columnFilters,
      get globalFilter() {
        return globalFilter;
      },
      set globalFilter(value) {
        setGlobalFilter(value);
      },
      columnVisibility,
    },
    columns,
    filterFns: {
      fuzzy: fuzzyFilter,
    },
  });

  return useMemo(
    () => ({
      loading: data.isFetching,
      table,
    }),
    [data.data, data.isFetching]
  );
};
