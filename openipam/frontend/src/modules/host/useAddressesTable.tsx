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
import { useMemo, useState } from "react";
import React from "react";
import { fuzzyFilter } from "../../components/filters";
import { useNavigate } from "react-router";
import { ActionsColumn } from "../../components/actionsColumn";

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
  const navigate = useNavigate();
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

  const addresses = useMemo<Address[]>(() => {
    if (!data.data) {
      return [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  const columns: ColumnDef<Address>[] = [
    ...ActionsColumn({
      size: 100,
      data,
      onView: (row) => {
        navigate(`/addresses/${row.name}`);
      },
    }),
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
    data: addresses,
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

  return useMemo(() => ({ table, loading: false }), [p.data]);
};
