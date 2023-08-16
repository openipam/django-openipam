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
import { betweenDatesFilter, fuzzyFilter } from "../../components/filters";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Domain } from "../../utils/types";
import { useInfiniteDomains } from "../../hooks/queries/useInfiniteDomains";
import { ActionsColumn } from "../../components/actionsColumn";

//TODO search permissions

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
    ...ActionsColumn({
      size: 100,
      data,
      onAdd: () => {
        p.setShowAddDomain((prev: boolean) => !prev);
      },
      onView: (row: any) => {
        navigate(`/domains/${row.name}`);
      },
      onEdit: (row: any) => {
        p.setEditDomain({
          show: true,
          domainData: row,
        });
      },
    }),
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
