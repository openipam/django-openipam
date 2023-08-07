import {
  ColumnDef,
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
import React from "react";
import { fuzzyFilter } from "../../components/filters";

type Address = {
  name: string;
  is_leased: boolean;
};

export const useAddressesTable = (p: {
  data: {
    static: string[];
    leased: string[];
  };
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Address[]>([]);

  const data = useMemo(() => {
    return {
      data: {
        pages: [
          {
            results: p.data.static.map((address) => ({
              name: address,
              is_leased: false,
            })),
          },
          {
            results: p.data.leased.map((address) => ({
              name: address,
              is_leased: true,
            })),
          },
        ],
      },
      hasNextPage: false,
      isFetchingNextPage: false,
      fetchNextPage: undefined,
    };
  }, [p.data]);

  const domains = useMemo<Address[]>(() => {
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

  const columns: ColumnDef<Address>[] = [
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
            {/* <button
              className="btn btn-circle btn-ghost btn-xs mt-1"
              onClick={() => data.fetchNextPage?.()}
              disabled={!data.hasNextPage || data.isFetchingNextPage}
            >
              <ExpandMore />
            </button> */}
          </div>
          {/* <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setShowAddDomain((prev: boolean) => !prev);
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
          {/* <button
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
          </button> */}
        </div>
      ),
    },
    {
      id: "name",
      header: "Name",
      accessorFn: (row) => row.name,
      meta: {
        filterType: "string",
      },
    },
    {
      id: "is_leased",
      header: "Type",
      accessorFn: (row) => (row.is_leased ? "Leased" : "Static"),
      meta: {
        filterType: "exact",
        filterOptions: ["Leased", "Static"],
      },
    },
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

  return useMemo(() => ({ table, loading: false }), [table]);
};
