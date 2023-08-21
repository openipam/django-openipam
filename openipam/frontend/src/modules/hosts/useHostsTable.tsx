import { ColumnFiltersState } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { Host } from "../../utils/types";
import { useInfiniteHosts } from "../../hooks/queries/useInfiniteHosts";
import { HostTableActions } from "./hostTableActions";
import { HostTableColumns } from "./hostTableColumns";
import { CreateTable } from "../../components/createTable";
import { useAuth } from "../../hooks/useAuth";

//TODO disabled columns only shows for admins.

export const useHostsTable = (p: {
  setShowAddHost: React.Dispatch<React.SetStateAction<boolean>>;
  setEditHost: React.Dispatch<
    React.SetStateAction<{ show: boolean; HostData: Host | undefined }>
  >;
  setRenewModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; data: Host[] | undefined }>
  >;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Host[] | undefined;
      title: string;
      onSubmit?: (data: Host[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  setAttributeModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Host[] | undefined;
      delete?: boolean;
    }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [prevData, setPrevData] = useState<Host[]>([]);
  const auth = useAuth();

  const data = useInfiniteHosts({
    ...Object.fromEntries(
      columnFilters
        .map((filter) => [
          filter.id,
          filter.value as string | number | string[],
        ])
        .map(([key, val]) => {
          switch (key) {
            case "expires":
              return [];
            case "mac":
              return [`mac`, val ?? ""];
            case "hostname":
              return [`hostname`, val ?? ""];
            case "group_owners":
              return [`group`, val ?? ""];
            case "user_owners":
              return [`user`, val ?? ""];
            case "disabled_host":
              return [`disabled`, val];
            case "ip_addresses":
              return [`ip_address`, val ?? ""];
            default:
              return [key, val ?? ""];
          }
        })
    ),
    expires__gt: (columnFilters.find((filter) => filter.id === "expires")
      ?.value as (string | undefined)[])?.[0],
    expires__lt: (columnFilters.find((filter) => filter.id === "expires")
      ?.value as (string | undefined)[])?.[1],
  });

  const Hosts = useMemo<Host[]>(() => {
    if (data.isFetching) {
      return [];
    }
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [
        ...data.data.pages.flatMap((page) => page.results ?? []),
      ]);
    }
  }, [data.data]);

  const table = CreateTable({
    data: Hosts,
    setColumnFilters: setColumnFilters,
    setRowSelection: setRowSelection,
    state: {
      columnFilters,
      rowSelection,
    },
    meta: {
      trProps: (row: any) => {
        return {
          className:
            row.expires && new Date(row.expires) < new Date()
              ? "bg-red-500 bg-opacity-70"
              : "",
        };
      },
      rowActions: (rows: Host[]) => {
        return (
          <HostTableActions
            rows={rows}
            table={table}
            setActionModule={p.setActionModule}
            setRenewModule={p.setRenewModule}
            setAttributeModule={p.setAttributeModule}
          />
        );
      },
    },
    columns: HostTableColumns({
      data,
      setShowAddHost: p.setShowAddHost,
      setEditHost: p.setEditHost,
      setRenewModule: p.setRenewModule,
      setActionModule: p.setActionModule,
      auth,
    }),
  });

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
    Hosts,
    data.data,
  ]);
};
