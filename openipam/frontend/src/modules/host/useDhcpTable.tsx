import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import React from "react";
import { DhcpRecord } from "../../utils/types";
import { useNavigate } from "react-router-dom";
import { useInfiniteHostDhcpRecords } from "../../hooks/queries/useInfiniteHostDhcpRecords";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";

const DhcpLookupKeys = ["host", "ip_content"];

export const useDhcpTable = (p: {
  host?: string;
  mac?: string;
  owner: boolean;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<DhcpRecord[]>([]);
  const navigate = useNavigate();
  const data = useInfiniteHostDhcpRecords({
    host: p.host,
    mac: p.mac,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => DhcpLookupKeys.includes(f.id))
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
  const dns = useMemo<DhcpRecord[]>(() => {
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
      data,
      onView: (row) => {
        navigate(`/domains/${row.domain}`);
      },
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "domain",
          header: "Domain",
          accessorFn: (row) => row.domain,
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
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    data: dns,
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
