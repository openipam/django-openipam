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
import { Add, Edit, ExpandMore, Visibility } from "@mui/icons-material";
import { Network } from "../../utils/types";
import { useNavigate } from "react-router-dom";
import { useInfiniteNetworks } from "../../hooks/queries/useInfiniteNetworks";
import { ActionsColumn } from "../../components/actionsColumn";

const NetworkLookupKeys = ["network", "name", "gateway", "description"];

export const useNetworksTable = (p: {
  setShowModule: any;
  setEditModule: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
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
          meta: {
            filterType: "string",
          },
        },
        {
          id: "name",
          header: "Name",
          accessorFn: (row) => row.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "gateway",
          header: "Gateway",
          accessorFn: (row) => row.gateway,
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
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "shared_network",
          header: "Shared Network",
          accessorFn: (row) => row.shared_network?.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "vlans",
          header: "Vlans",
          accessorFn: (row) => row.vlans?.length ?? "0",
          meta: {
            filterType: "string",
          },
        },
        {
          id: "buildings",
          header: "Buildings",
          accessorFn: (row) => row.buildings?.length ?? "0",
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
