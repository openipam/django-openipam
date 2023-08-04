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
import { betweenDatesFilter, fuzzyFilter } from "../../components/filters";
import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Add, Edit, ExpandMore, Visibility } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { Host } from "../../utils/types";
import { BooleanRender, booleanAccessor } from "../../components/boolean";

//TODO search permissions

const getList = (obj: Record<string, string>) => {
  return (
    <div className="">
      {Object.entries(obj ?? {}).map(([key, val]) => (
        <div key={Math.random()}>
          <div key={Math.random()} className="font-bold">
            {key}:
          </div>
          <div key={Math.random()} className="">
            {" "}
            {val}
          </div>
        </div>
      ))}
    </div>
  );
};

export const useInfiniteHosts = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["Hosts, all", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.hosts.get({ page: pageParam, ...p });
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

export const useHostsTable = () => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Host[]>([]);
  const navigate = useNavigate();

  const data = useInfiniteHosts({
    ...Object.fromEntries(
      columnFilters.map((filter) => [
        filter.id,
        filter.value as string | number,
      ])
    ),
  });
  const Hosts = useMemo<Host[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.results)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<Host>();
  const columns = [
    {
      size: 50,
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
          {/* <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setShowAddHost((prev: boolean) => !prev);
            }}
          >
            <Add />
          </button> */}
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
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => navigate(`/Hosts/${row.original.mac}`)}
            disabled={!row.original.mac}
          >
            <Visibility fontSize="small" />
          </button>
          {/* <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setEditHost({
                show: true,
                HostData: row.original,
              });
            }}
          >
            <Edit fontSize="small" />
          </button> */}
        </div>
      ),
    },
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "mac",
          header: "Mac",
          accessorFn: (row) => row.mac,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "hostname",
          header: "Hostname",
          accessorFn: (row) => row.hostname,
          meta: {
            filterType: "string",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Primary Details",
      header: "Primary Details",
      columns: [
        {
          id: "expires",
          header: "Expires",
          accessorFn: (row) =>
            row.expires
              ? new Date(row.expires).toISOString().split("T")[0]
              : null,
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
        },
        // {
        //   id: "description",
        //   size: 200,
        //   header: "Description",
        //   accessorFn: (row) => row.description,
        //   meta: {
        //     filterType: "string",
        //   },
        // },
        {
          id: "master_ip_address",
          header: "Master IP Address",
          accessorFn: (row) => row.master_ip_address,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group?.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "disabled_host",
          size: 50,
          header: "Disabled Host",
          accessorFn: booleanAccessor("disabled_host"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_dynamic",
          size: 50,
          header: "Dynamic",
          cell: BooleanRender,
          accessorFn: booleanAccessor("is_dynamic"),
          meta: {
            filterType: "boolean",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Owners",
      header: "Owners",
      columns: [
        {
          id: "user_owners",
          header: "User Owners",
          size: 200,
          accessorFn: (row) => row.user_owners?.join(",\n"),
          meta: {
            filterType: "string",
          },
        },
        {
          id: "group_owners",
          header: "Group Owners",
          size: 200,
          accessorFn: (row) => row.group_owners?.join(",\n"),
          meta: {
            filterType: "string",
          },
        },
      ],
    }),
    // columnHelper.group({
    //   id: "Changed",
    //   header: "Changed",
    //   columns: [
    //     {
    //       id: "changed",
    //       header: "Last Changed",
    //       accessorFn: (row) =>
    //         row.changed
    //           ? new Date(row.changed).toISOString().split("T")[0]
    //           : null,
    //       meta: {
    //         filterType: "date",
    //       },
    //       filterFn: betweenDatesFilter,
    //     },
    //     {
    //       id: "changedBy",
    //       header: "Changed By",
    //       accessorFn: (row) => row.changed_by.username,
    //       meta: {
    //         filterType: "string",
    //       },
    //     },
    //   ],
    // }),
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
    data: Hosts,
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

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};
