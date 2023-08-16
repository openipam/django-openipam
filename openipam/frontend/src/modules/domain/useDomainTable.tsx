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
import { fuzzyFilter } from "../../components/filters";
import React from "react";
import { DNS_TYPES, DnsRecord } from "../../utils/types";
import { useInfiniteDnsRecords } from "../../hooks/queries/useInfiniteDnsRecords";
import { ActionsColumn } from "../../components/actionsColumn";

//TODO search permissions

const DNSLookupKeys = ["name", "content", "dns_type", "host"];

export const useDomainTable = (p: {
  domain: string;
  setShowModule: any;
  setEditModule: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<DnsRecord[]>([]);

  const data = useInfiniteDnsRecords({
    domain: p.domain,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => DNSLookupKeys.includes(f.id))
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
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
    ...ActionsColumn({
      size: 80,
      onAdd: () => {
        p.setShowModule(true);
      },
      data,
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          DnsData: row,
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
          id: "content",
          header: "Content",
          cell: ({ row }: { row: { original: DnsRecord } }) => {
            return row.original.dns_type === "A" ? (
              <a
                className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                href={`#/addresses/${row.original.content}`}
              >
                {row.original.content}
              </a>
            ) : (
              row.original.content
            );
          },
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
          id: "dns_type",
          header: "Type",
          accessorFn: (row) => row.dns_type,
          meta: {
            filterType: "exact",
            filterOptions: DNS_TYPES,
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
          cell: ({ row }: { row: { original: DnsRecord } }) => {
            return (
              <a
                className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                href={`#/hosts/${row.original.host}`}
              >
                {row.original.host}
              </a>
            );
          },
          accessorFn: (row) => row.host,
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
    enableColumnResizing: true,
    columnResizeMode: "onChange",
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
