import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import { betweenDatesFilter } from "../../components/table/filters";
import React from "react";
import { DhcpRecord } from "../../utils/types";
import { useNavigate } from "react-router-dom";
import { useInfiniteDhcpRecords } from "../../hooks/queries/useInfiniteDhcpRecords";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";

const DhcpLookupKeys = ["host", "ip_content"];

export const useDhcpTable = (p: { domain: string }) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<DhcpRecord[]>([]);
  const navigate = useNavigate();
  const data = useInfiniteDhcpRecords({
    ...p,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => DhcpLookupKeys.includes(f.id))
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
  const dhcp = useMemo<DhcpRecord[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.dhcp);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.dhcp)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<DhcpRecord>();
  const columns = [
    ...ActionsColumn({
      size: 100,
      onView: (row) => {
        navigate(`/hosts/${row.host}`);
      },
      data,
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "host",
          header: "Host",
          accessorFn: (row) => row.host,
        },
        {
          id: "ip_content",
          header: "IP Content",
          cell: ({ row }: { row: { original: DhcpRecord } }) => {
            return (
              <a
                className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                href={`#/addresses/${row.original.ip_content}`}
              >
                {row.original.ip_content}
              </a>
            );
          },
          accessorFn: (row) => row.ip_content,
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "ttl",
          header: "TTL",
          accessorFn: (row) => row.ttl,
        },
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) =>
            row.changed
              ? new Date(row.changed).toISOString().split("T")[0]
              : "",
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    data: dhcp,
    state: {
      columnFilters,
    },
    columns,
  });

  return useMemo(
    () => ({
      loading: data.isFetching,
      table,
    }),
    [data.data, data.isFetching]
  );
};
