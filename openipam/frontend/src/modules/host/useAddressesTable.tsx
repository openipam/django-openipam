import { ColumnDef, ColumnFiltersState } from "@tanstack/react-table";
import { useMemo, useState } from "react";
import React from "react";
import { useNavigate } from "react-router";
import { ActionsColumn } from "../../components/actionsColumn";
import { CreateTable } from "../../components/createTable";

type Address = {
  name: string;
  is_leased: boolean;
};

export const useAddressesTable = (p: {
  data: {
    static: string[];
    leased: string[];
  };
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const navigate = useNavigate();
  const data = useMemo(() => {
    return {
      data: {
        pages: [
          {
            results: p.data.static.map((address) => ({
              name: address,
              is_leased: false,
            })),
          },
          {
            results: p.data.leased.map((address) => ({
              name: address,
              is_leased: true,
            })),
          },
        ],
      },
      hasNextPage: false,
      isFetchingNextPage: false,
      fetchNextPage: undefined,
    };
  }, [p.data]);

  const addresses = useMemo<Address[]>(() => {
    if (!data.data) {
      return [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  const columns: ColumnDef<Address>[] = [
    ...ActionsColumn({
      size: 100,
      data,
      onView: (row) => {
        navigate(`/addresses/${row.name}`);
      },
    }),
    {
      id: "name",
      header: "Name",
      accessorFn: (row) => row.name,
    },
    {
      id: "is_leased",
      header: "Type",
      accessorFn: (row) => (row.is_leased ? "Leased" : "Static"),
      meta: {
        filterType: "exact",
        filterOptions: ["Leased", "Static"],
      },
    },
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    setGlobalFilter: setGlobalFilter,
    data: addresses,
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

  return useMemo(() => ({ table, loading: false }), [p.data]);
};
