import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import React from "react";
import { Network } from "../../utils/types";
import { useNavigate } from "react-router-dom";
import { useInfiniteNetworks } from "../../hooks/queries/useInfiniteNetworks";
import { ActionsColumn } from "../../components/actionsColumn";
import { CreateTable } from "../../components/createTable";

const NetworkLookupKeys = ["network", "name", "gateway", "description"];

export const useNetworksTable = (p: {
  setShowModule: any;
  setEditModule: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [prevData, setPrevData] = useState<Network[]>([]);

  const data = useInfiniteNetworks({
    ...Object.fromEntries(Object.entries(p).filter(([_, v]) => v)),
    ...Object.fromEntries(
      columnFilters
        .filter((f) => NetworkLookupKeys.includes(f.id) && f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
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
      onAdd: () => {
        p.setShowModule(true);
      },
      onView: (row) => {
        navigate(`/networks/${row.network}`);
      },
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          Network: row.network,
        });
      },
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
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    setGlobalFilter: setGlobalFilter,
    data: dns,
    state: {
      columnFilters,
      get globalFilter() {
        return globalFilter;
      },
      set globalFilter(value) {
        setGlobalFilter(value);
      },
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
