import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import React from "react";
import { Log, LogActions, LogTypes } from "../../utils/types";
import { useInfiniteLogs } from "../../hooks/queries/useInfiniteLogs";
import { ActionsColumn } from "../../components/actionsColumn";
import { CreateTable } from "../../components/createTable";

//TODO search permissions

const logSearchFields = ["user", "action_flag"];

export const useLogsTable = () => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<Log[]>([]);
  const [emailView, setEmailView] = useState<boolean>(false);

  useEffect(() => {
    setEmailView(
      !!columnFilters.filter((f) => f.id === "type" && f.value === "email")
        .length
    );
  }, [columnFilters]);

  const data = useInfiniteLogs({
    ...Object.fromEntries(
      columnFilters
        .filter(
          (f) =>
            logSearchFields.includes(f.id) ||
            (f.id === "type" &&
              LogTypes.includes(f.value as typeof LogTypes[number]))
        )
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
  const logs = useMemo<Log[]>(() => {
    if (data.isFetching) {
      return [];
    }
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.logs ?? page.emails);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.logs)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<Log>();
  const columns = [
    ...ActionsColumn({
      data,
      size: 50,
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "type",
          header: "Type",
          accessorFn: (row) => row.content_type ?? "email",
          meta: {
            filterType: "exact",
            filterOptions: LogTypes.map((type) => type),
          },
        },
        {
          id: emailView ? "to" : "user",
          header: emailView ? "To" : "User",
          accessorFn: (row) => row.user ?? row.to,
        },
      ],
    }),
    emailView
      ? columnHelper.group({
          id: "Email Details",
          header: "Email Details",
          columns: [
            {
              id: "subject",
              header: "Subject",
              accessorFn: (row) => row.subject,
              meta: {
                filterType: "string",
              },
            },
            {
              id: "body",
              header: "Body",
              accessorFn: (row) => row.body?.slice(0, 50) + "...",
              meta: {
                filterType: "string",
              },
            },
          ],
        })
      : columnHelper.group({
          id: "Other Details",
          header: "Other Details",
          columns: [
            {
              id: "action_flag",
              header: "Action",
              accessorFn: (row) => row.action_flag,
              meta: {
                filterType: "exact",
                filterOptions: LogActions.map((action) => action),
              },
            },
            {
              id: "action_time",
              header: "Time",
              accessorFn: (row) => row.action_time,
              meta: {
                filterType: "string",
              },
            },
            {
              id: "object_repr",
              header: "Object",
              accessorFn: (row) => row.object_repr,
              meta: {
                filterType: "string",
              },
            },
            {
              id: "change_message",
              header: "Message",
              accessorFn: (row) => row.change_message,
              meta: {
                filterType: "string",
              },
            },
          ],
        }),
  ];

  const table = CreateTable({
    setColumnFilters: setColumnFilters,
    data: logs,
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
    [data.data, logs, data.isFetching, columns]
  );
};
