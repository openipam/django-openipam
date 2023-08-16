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
import { fuzzyFilter } from "./filters";

export const CreateTable = (p: {
  setColumnFilters: React.Dispatch<React.SetStateAction<ColumnFiltersState>>;
  setGlobalFilter: React.Dispatch<React.SetStateAction<undefined>>;
  setRowSelection?: React.Dispatch<React.SetStateAction<{}>>;
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
    // Sorting
    getSortedRowModel: getSortedRowModel(),
    // Filters
    onColumnFiltersChange: p.setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    onGlobalFilterChange: p.setGlobalFilter,
    globalFilterFn: fuzzyFilter,
    // Row Selection
    enableRowSelection: true,
    enableMultiRowSelection: true,
    ...(p.setRowSelection ? { onRowSelectionChange: p.setRowSelection } : {}),
    data: p.data,
    state: p.state,
    ...(p.meta ? { meta: p.meta } : {}),
    columns: p.columns,
    filterFns: {
      fuzzy: fuzzyFilter,
    },
  });
};
