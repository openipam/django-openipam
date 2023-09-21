import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { Network } from "../../utils/types";
import { useNavigate } from "react-router-dom";
import { useInfiniteNetworks } from "../../hooks/queries/useInfiniteNetworks";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { getOrdering } from "../../components/table/getOrdering";
import { NetworksTableActions } from "./networksTableActions";

const NetworkLookupKeys = ["network", "name", "gateway", "description"];

export const useNetworksTable = (p: {
  setShowModule: React.Dispatch<React.SetStateAction<boolean>>;
  setEditModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; network: Network | undefined }>
  >;
  onSelectColumns: () => void;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Network[] | undefined;
      title: string;
      onSubmit?: (data: Network[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<Network[]>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [pageSize, setPageSize] = useState<number>(10);
  const [page, setPage] = useState<number>(1);
  const [columnVisibility, setColumnVisibility] = useState<any[]>(
    localStorage.getItem("networksTableColumns")
      ? JSON.parse(localStorage.getItem("networksTableColumns")!)
      : {
          changed: false,
          changed_by: false,
          dhcp_group: false,
        }
  );
  useEffect(() => {
    localStorage.setItem(
      "networksTableColumns",
      JSON.stringify(columnVisibility)
    );
  }, [columnVisibility]);
  const data = useInfiniteNetworks({
    ...Object.fromEntries(
      columnFilters
        .filter((f) => NetworkLookupKeys.includes(f.id) && f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
    page,
    page_size: pageSize,
    ordering: getOrdering(columnSort),
  });
  const dns = useMemo<Network[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.networks);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.networks)]);
    }
  }, [data.data]);
  const navigate = useNavigate();
  const columnHelper = createColumnHelper<Network>();
  const columns = [
    ...ActionsColumn({
      data,
      size: 80,
      pageSize,
      setPageSize,
      onAdd: () => {
        p.setShowModule(true);
      },
      onView: (row) => {
        navigate(`/networks/${row.network}`);
      },
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          network: row.network,
        });
      },
      onSelectColumns: p.onSelectColumns,
      enableSelection: true,
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "network",
          header: "Network",
          accessorFn: (row) => row.network,
        },
        {
          id: "name",
          header: "Name",
          accessorFn: (row) => row.name,
        },
        {
          id: "gateway",
          header: "Gateway",
          accessorFn: (row) => row.gateway,
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
        },
        {
          id: "shared_network",
          header: "Shared Network",
          accessorFn: (row) => row.shared_network?.name,
        },

        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group,
        },
        {
          id: "vlans",
          header: "Vlans",
          accessorFn: (row) => row.vlans?.length ?? "0",
        },
        {
          id: "buildings",
          header: "Buildings",
          accessorFn: (row) => row.buildings?.length ?? "0",
        },
      ],
    }),
    columnHelper.group({
      id: "Changed",
      header: "Changed",
      columns: [
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) => row.changed,
        },
        {
          id: "changed_by",
          header: "Changed By",
          accessorFn: (row) => row.changed_by?.username,
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters,
    setRowSelection,
    setColumnSort,
    setColumnVisibility,
    data: dns,
    state: {
      columnFilters,
      rowSelection,
      pageSize,
      sorting: columnSort,
      columnVisibility,
    },
    columns,
    orderingColumns: ["network", "name", "changed"],
    meta: {
      total: data.data?.pages?.[0]?.count,
      pageSize,
      page,
      setPage,
      rowActions: (rows: Network[]) => {
        return (
          <NetworksTableActions
            rows={rows}
            table={table}
            setActionModule={p.setActionModule}
          />
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
