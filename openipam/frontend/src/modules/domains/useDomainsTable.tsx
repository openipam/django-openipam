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

//TODO search permissions, add, edit

type Domain = {
  id: number;
  name: string;
  description: string;
  changed_by: string;
  master: string;
  changed: string;
  user_perms: Record<string, string>;
  group_perms: Record<string, string>;
};

const getPerms = (perms: Record<string, string>) => {
  return (
    <div className="">
      {Object.entries(perms ?? {}).map(([key, val]) => (
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

export const useInfiniteDomains = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["domains, all", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.domains.get({ page: pageParam, ...p });
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

export const useDomainsTable = (p: {
  setShowAddDomain: any;
  setEditDomain: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Domain[]>([]);
  const navigate = useNavigate();

  const data = useInfiniteDomains({
    ...Object.fromEntries(
      columnFilters.map((filter) => [
        filter.id,
        filter.value as string | number,
      ])
    ),
  });
  const domains = useMemo<Domain[]>(() => {
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

  const columnHelper = createColumnHelper<Domain>();
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
              p.setShowAddDomain((prev: boolean) => !prev);
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
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => navigate(`/domains/${row.original.name}`)}
            disabled={!row.original.name}
          >
            <Visibility fontSize="small" />
          </button>
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setEditDomain({
                show: true,
                domainData: row.original,
              });
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
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
          meta: {
            filterType: "string",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Permissions",
      header: "Permissions",
      columns: [
        {
          id: "user_perms",
          size: 200,
          header: "User Permissions",
          cell: ({ row }: { row: any }) => {
            return getPerms(row.original.user_perms);
          },
          meta: {
            filterType: "string",
          },
        },
        {
          id: "group_perms",
          size: 200,
          header: "Group Permissions",
          cell: ({ row }: { row: any }) => {
            return getPerms(row.original.group_perms);
          },
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
          id: "master",
          header: "Master",
          accessorFn: (row) => row.master,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "changed",
          header: "Last Changed",
          accessorFn: (row) =>
            row.changed
              ? new Date(row.changed).toISOString().split("T")[0]
              : null,
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
        },
        {
          id: "changedBy",
          header: "Changed By",
          accessorFn: (row) => row.changed_by,
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
    data: domains,
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