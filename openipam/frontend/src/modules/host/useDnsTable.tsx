import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useContext, useEffect, useMemo, useState } from "react";
import React from "react";
import { DNS_TYPES, DnsRecord } from "../../utils/types";
import { useInfiniteHostDnsRecords } from "../../hooks/queries/useInfiniteHostDnsRecords";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useApi } from "../../hooks/useApi";
import { ThemeContext } from "../../hooks/useTheme";

const DNSLookupKeys = ["name", "content", "dns_type"];

export const useDnsTable = (p: {
  host?: string;
  mac?: string;
  setShowModule: any;
  setEditModule: any;
  owner: boolean;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: DnsRecord[] | undefined;
      title: string;
      onSubmit?: (data: DnsRecord[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<DnsRecord[]>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [action, setAction] = useState<string>("delete");
  const api = useApi();

  const data = useInfiniteHostDnsRecords({
    ...Object.fromEntries(Object.entries(p).filter(([_, v]) => v)),
    ...Object.fromEntries(
      columnFilters
        .filter((f) => DNSLookupKeys.includes(f.id) && f.value)
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
  const { theme } = useContext(ThemeContext);
  const columnHelper = createColumnHelper<DnsRecord>();
  const columns = [
    ...ActionsColumn({
      size: 80,
      data,
      ...(p.owner
        ? {
            onAdd: () => {
              p.setShowModule(true);
            },
            enableSelection: true,
          }
        : {}),
      ...(p.owner
        ? {
            onEdit: (row) => {
              p.setEditModule({
                show: true,
                DnsData: row.original,
              });
            },
          }
        : {}),
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "name",
          header: "Name",
          accessorFn: (row) => row.name,
        },
        {
          id: "content",
          header: "Content",
          cell: ({ row }: { row: { original: DnsRecord } }) => {
            return row.original.dns_type === "A" ? (
              <a
                className={`${
                  theme === "dark" ? "text-secondary" : "text-primary"
                } hover:underline btn btn-sm btn-ghost`}
                href={`#/addresses/${row.original.content}`}
              >
                {row.original.content}
              </a>
            ) : (
              row.original.content
            );
          },
          accessorFn: (row) => row.content,
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
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    setRowSelection: setRowSelection,
    data: dns,
    state: {
      columnFilters,
      rowSelection,
    },
    columns,
    meta: {
      rowActions: (rows: DnsRecord[]) => {
        return (
          <div className="flex flex-col gap-2 m-2">
            <label>Actions</label>
            <div className="flex flex-row gap-2">
              <select
                id={`actions`}
                onChange={(v) => {
                  setAction(v.target.value);
                }}
                value={action}
                className="rounded-md p-2 select select-bordered w-full"
              >
                {Object.entries(actions).map(([key, value]) => (
                  <option value={key} key={key}>
                    {value}
                  </option>
                ))}
              </select>
              <button
                className="btn btn-primary"
                onClick={() => {
                  switch (action) {
                    case "delete":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Delete Records",
                        onSubmit: () => {
                          rows.forEach((row) => {
                            api.dns.byId(row.id).delete();
                          });
                        },
                        children: <div></div>,
                      });
                      break;
                    default:
                      break;
                  }
                }}
                disabled={rows.length === 0}
              >
                Go
              </button>
            </div>
          </div>
        );
      },
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

const actions = {
  delete: "Delete",
};
