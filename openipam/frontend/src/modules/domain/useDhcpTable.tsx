import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
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
  const [pageSize, setPageSize] = useState<number>(10);
  const [page, setPage] = useState<number>(1);
  const navigate = useNavigate();
  const data = useInfiniteDhcpRecords({
    ...p,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => DhcpLookupKeys.includes(f.id))
        .map((filter) => [filter.id, filter.value as string])
    ),
    page,
    page_size: pageSize,
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
      pageSize,
      setPageSize,
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
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    data: dhcp,
    meta: {
      total: data.data?.pages?.[0]?.count,
      page,
      pageSize,
      setPage,
      setPageSize,
    },
    state: {
      columnFilters,
      pageSize,
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
