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
import {
  betweenDatesFilter,
  fuzzyFilter,
} from "../../components/table/filters";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Domain } from "../../utils/types";
import { useInfiniteDomains } from "../../hooks/queries/useInfiniteDomains";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useAuth } from "../../hooks/useAuth";

//TODO search permissions

const getPerms = (perms: Record<string, string>) => {
  return (
    <div className="">
      {Object.entries(perms ?? {}).map(([key, val]) => (
        <div key={Math.random()}>
          <div key={Math.random()} className="font-bold">
            {key}:
          </div>
          <div key={Math.random()} className="">
            {" "}
            {val}
          </div>
        </div>
      ))}
    </div>
  );
};

export const useDomainsTable = (p: {
  setShowAddDomain: any;
  setEditDomain: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<Domain[]>([]);
  const navigate = useNavigate();
  const auth = useAuth();

  const data = useInfiniteDomains({
    ...Object.fromEntries(
      columnFilters.map((filter) => [
        filter.id,
        filter.value as string | number,
      ])
    ),
  });
  const domains = useMemo<Domain[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.results)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<Domain>();
  const columns = [
    ...(auth?.is_ipamadmin
      ? ActionsColumn({
          size: 100,
          data,
          onAdd: () => {
            p.setShowAddDomain((prev: boolean) => !prev);
          },
          onView: (row: any) => {
            navigate(`/domains/${row.name}`);
          },
          onEdit: (row: any) => {
            p.setEditDomain({
              show: true,
              domainData: row,
            });
          },
        })
      : ActionsColumn({
          size: 90,
          data,
          onView: (row: any) => {
            navigate(`/domains/${row.name}`);
          },
        })),
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
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
        },
      ],
    }),
    columnHelper.group({
      id: "Permissions",
      header: "Permissions",
      columns: [
        {
          id: "user_perms",
          size: 200,
          header: "User Permissions",
          cell: ({ row }: { row: any }) => {
            return getPerms(row.original.user_perms);
          },
        },
        {
          id: "group_perms",
          size: 200,
          header: "Group Permissions",
          cell: ({ row }: { row: any }) => {
            return getPerms(row.original.group_perms);
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "master",
          header: "Master",
          accessorFn: (row) => row.master,
        },
        {
          id: "changed",
          header: "Last Changed",
          accessorFn: (row) =>
            row.changed
              ? new Date(row.changed).toISOString().split("T")[0]
              : null,
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
        },
        {
          id: "changedBy",
          header: "Changed By",
          accessorFn: (row) => row.changed_by,
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    data: domains,
    state: {
      columnFilters,
    },
    columns,
  });

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};
