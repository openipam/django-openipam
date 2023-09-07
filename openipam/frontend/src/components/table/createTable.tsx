import {
  ColumnFiltersState,
  getCoreRowModel,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import React from "react";

export const CreateTable = (p: {
  setColumnFilters: React.Dispatch<React.SetStateAction<ColumnFiltersState>>;
  setRowSelection?: React.Dispatch<React.SetStateAction<{}>>;
  setGlobalFilter?: React.Dispatch<React.SetStateAction<any[]>>;
  setColumnSort?: React.Dispatch<React.SetStateAction<any[]>>;
  setColumnVisibility?: React.Dispatch<React.SetStateAction<any>>;
  data: any;
  state: any;
  meta?: any;
  columns: any;
}) => {
  return useReactTable({
    getCoreRowModel: getCoreRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    onColumnVisibilityChange: p.setColumnVisibility,
    // Sorting
    onSortingChange: p.setColumnSort,
    // Filters
    onColumnFiltersChange: p.setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    // Global Filter
    onGlobalFilterChange: p.setGlobalFilter,
    // Row Selection
    enableRowSelection: true,
    enableFilters: false,
    enableMultiRowSelection: true,
    ...(p.setRowSelection ? { onRowSelectionChange: p.setRowSelection } : {}),
    data: p.data,
    state: p.state,
    ...(p.meta ? { meta: p.meta } : {}),
    columns: p.columns.map((c: any) => ({
      ...c,
      columns:
        c.columns?.map((c: any) => ({
          ...c,
          filterFn: undefined,
          sortingFn: undefined,
        })) ?? [],
    })),
    sortingFns: undefined,
  });
};
