import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import React from "react";
import { User } from "../../utils/types";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useInfiniteUsers } from "../../hooks/queries/useInfiniteUsers";
import { BooleanRender, booleanAccessor } from "../../components/table/boolean";

export const useUsersTable = (p: {}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<User[]>([]);
  const data = useInfiniteUsers({});
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
