import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import React from "react";
import { Address } from "../../utils/types";
import { BooleanRender, booleanAccessor } from "../../components/table/boolean";
import { useInfiniteNetworkAddresses } from "../../hooks/queries/useInfiniteNetworkAddresses";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";

const AddressLookupKeys = ["address", "name", "gateway", "description"];

export const useAddressesTable = (p: {
  network: string;
  range: string;
  setShowModule: any;
  setEditModule: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<Address[]>([]);

  const data = useInfiniteNetworkAddresses({
    network: p.network,
    range: p.range,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => AddressLookupKeys.includes(f.id) && f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
  const dns = useMemo<Address[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.addresses);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.addresses)]);
    }
  }, [data.data]);
  const columnHelper = createColumnHelper<Address>();
  const columns = [
    ...ActionsColumn({
      data,
      size: 80,
      onAdd: () => {
        p.setShowModule(true);
      },
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          Address: row.address,
        });
      },
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "address",
          header: "Address",
          accessorFn: (row) => row.address,
        },
        {
          id: "host",
          header: "host",
          accessorFn: (row) => row.host,
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
          id: "reserved",
          header: "Reserved",
          accessorFn: booleanAccessor("reserved"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "pool",
          header: "Pool",
          accessorFn: (row) => row.pool?.name,
        },
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) =>
            row.changed ? new Date(row.changed).toLocaleString() : "",
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
