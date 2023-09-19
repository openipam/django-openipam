import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { User } from "../../utils/types";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useInfiniteUsers } from "../../hooks/queries/useInfiniteUsers";
import { BooleanRender, booleanAccessor } from "../../components/table/boolean";
import { getOrdering } from "../../components/table/getOrdering";
import { UserTableActions } from "./userTableActions";

export const useUsersTable = (p: {
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: User[] | undefined;
      title: string;
      onSubmit?: (data: User[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<User[]>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [pageSize, setPageSize] = useState<number>(25);
  const [page, setPage] = useState<number>(1);
  const data = useInfiniteUsers({
    ...Object.fromEntries(
      columnFilters
        .filter((f) => f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
    ordering: getOrdering(columnSort),
    page,
    page_size: pageSize,
  });
  const dns = useMemo<User[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.users);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.users)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<User>();
  const columns = [
    ...ActionsColumn({
      size: 100,
      data,
      pageSize,
      setPageSize,
      enableSelection: true,
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "username",
          header: "Username",
          accessorFn: (row) => row.username,
        },
        {
          id: "fullname",
          header: "Full Name",
          accessorFn: (row) => row.first_name + " " + row.last_name,
        },
        {
          id: "email",
          header: "Email",
          accessorFn: (row) => row.email,
        },
      ],
    }),
    columnHelper.group({
      id: "Permissions",
      header: "Permissions",
      columns: [
        {
          id: "is_staff",
          header: "Staff",
          accessorFn: booleanAccessor("is_staff"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_ipamadmin",
          header: "Admin",
          accessorFn: booleanAccessor("is_ipamadmin"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_superuser",
          header: "Superuser",
          accessorFn: booleanAccessor("is_superuser"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "groups",
          header: "groups",
          accessorFn: (row) => row.groups.join(", "),
        },
        {
          id: "last_login",
          header: "Last Login",
          accessorFn: (row) =>
            row.last_login
              ? new Date(row.last_login).toLocaleDateString()
              : null,
          meta: {
            filterType: "date",
          },
        },
        {
          id: "date_joined",
          header: "Date Joined",
          accessorFn: (row) =>
            row.date_joined
              ? new Date(row.date_joined).toLocaleDateString()
              : null,
          meta: {
            filterType: "date",
          },
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters,
    setRowSelection,
    setColumnSort,
    data: dns,
    state: {
      columnFilters,
      rowSelection,
      pageSize,
      sorting: columnSort,
    },
    columns,
    meta: {
      total: data.data?.pages?.[0]?.count,
      page,
      pageSize,
      setPage,
      rowActions: (rows: User[]) => {
        return (
          <UserTableActions
            rows={rows}
            table={table}
            setActionModule={p.setActionModule}
            refetch={data.refetch}
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
