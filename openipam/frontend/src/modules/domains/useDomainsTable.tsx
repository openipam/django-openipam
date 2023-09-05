import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Domain } from "../../utils/types";
import { useInfiniteDomains } from "../../hooks/queries/useInfiniteDomains";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useAuth } from "../../hooks/useAuth";
import { getOrdering } from "../../components/table/getOrdering";
import { useApi } from "../../hooks/useApi";

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
  onSelectColumns: () => void;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Domain[] | undefined;
      title: string;
      onSubmit?: (data: Domain[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<Domain[]>([]);
  const navigate = useNavigate();
  const auth = useAuth();
  const api = useApi();

  const [action, setAction] = useState<string>("delete");
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [pageSize, setPageSize] = useState<number>(10);
  const [page, setPage] = useState<number>(1);
  const [columnVisibility, setColumnVisibility] = useState<any>(
    localStorage.getItem("domainTableColumns")
      ? JSON.parse(localStorage.getItem("domainTableColumns")!)
      : {}
  );
  useEffect(() => {
    localStorage.setItem(
      "domainTableColumns",
      JSON.stringify(columnVisibility)
    );
  }, [columnVisibility]);
  const data = useInfiniteDomains({
    ...Object.fromEntries(
      columnFilters.map((filter) => [
        filter.id,
        filter.value as string | number,
      ])
    ),
    page,
    page_size: pageSize,
    ordering: getOrdering(columnSort),
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
          pageSize,
          setPageSize,
          enableSelection: true,
          onSelectColumns: p.onSelectColumns,
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
          meta: {
            hideFilter: true,
          },
        },
        {
          id: "group_perms",
          size: 200,
          header: "Group Permissions",
          cell: ({ row }: { row: any }) => {
            return getPerms(row.original.group_perms);
          },
          meta: {
            hideFilter: true,
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
    setRowSelection,
    setColumnSort,
    setColumnVisibility,
    data: domains,
    state: {
      columnFilters,
      rowSelection,
      pageSize,
      sorting: columnSort,
      columnVisibility,
    },
    meta: {
      total: data.data?.pages?.[0]?.count,
      page: page,
      setPage: setPage,
      pageSize,
      rowActions: (rows: Domain[]) => {
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
                            api.domains.byId(row.name).delete();
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
    columns,
  });

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};

const actions = {
  delete: "Delete",
};
