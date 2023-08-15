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
import { Address } from "../../utils/types";
import { useNavigate } from "react-router-dom";
import { BooleanRender, booleanAccessor } from "../../components/boolean";

const AddressLookupKeys = ["address", "name", "gateway", "description"];

export const useInfiniteAddresses = (p: {
  network: string;
  subnet: string;
  [key: string]: string | undefined;
}) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["network, Addresses", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.networks
        .byId(`${p.network}/${p.subnet}`)
        .addresses.get({ page: pageParam, ...p });
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

export const useAddressesTable = (p: {
  network: string;
  subnet: string;
  setShowModule: any;
  setEditModule: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Address[]>([]);

  const data = useInfiniteAddresses({
    network: p.network,
    subnet: p.subnet,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => AddressLookupKeys.includes(f.id) && f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
  const dns = useMemo<Address[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.addresses);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.addresses)]);
    }
  }, [data.data]);
  const navigate = useNavigate();
  const columnHelper = createColumnHelper<Address>();
  const columns = [
    {
      size: 80,
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
              p.setShowModule(true);
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
            onClick={() => navigate(`/Addresses/${row.original.Address}`)}
            disabled={!row.original.Address}
          >
            <Visibility fontSize="small" />
          </button> */}
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setEditModule({
                show: true,
                DnsData: row.original,
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
          id: "address",
          header: "Address",
          accessorFn: (row) => row.address,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "host",
          header: "host",
          accessorFn: (row) => row.host,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "gateway",
          header: "Gateway",
          accessorFn: (row) => row.gateway,
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
          id: "reserved",
          header: "Reserved",
          accessorFn: booleanAccessor("reserved"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "pool",
          header: "Pool",
          accessorFn: (row) => row.pool?.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) =>
            row.changed ? new Date(row.changed).toLocaleString() : "",
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
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
