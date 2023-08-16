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
import { ExpandMore } from "@mui/icons-material";
import { Log, LogActions, LogTypes } from "../../utils/types";
import { useInfiniteLogs } from "../../hooks/queries/useInfiniteLogs";

//TODO search permissions

const logSearchFields = ["user", "action_flag"];

export const useLogsTable = () => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
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
    {
      size: 100,
      enableHiding: false,
      enableSorting: false,
      enableColumnFilter: false,
      id: "actions",
      header: ({ table }: any) => (
        <div className="flex gap-1 items-center relative">
          {/* <PlainIndeterminateCheckbox
                checked={table.getIsAllRowsSelected()}
                indeterminate={table.getIsSomeRowsSelected()}
                onChange={table.getToggleAllRowsSelectedHandler()}
              /> */}
          <div className="tooltip tooltip-right" data-tip="Load More">
            <button
              className="btn btn-circle btn-ghost btn-xs mt-1"
              onClick={() => data.fetchNextPage?.()}
              disabled={!data.hasNextPage || data.isFetchingNextPage}
            >
              <ExpandMore />
            </button>
          </div>
        </div>
      ),
      cell: ({ row }: { row: any }) => (
        <div className="flex gap-1 items-center">
          {/* <PlainIndeterminateCheckbox
                checked={row.getIsSelected()}
                onChange={row.getToggleSelectedHandler()}
                disabled={!row.getCanSelect()}
                indeterminate={row.getIsSomeSelected()}
              /> */}
          {/* <button
            className="btn btn-circle btn-ghost btn-xs"
            // onClick={() => navigate(`/domain/${row.original.name}`)}
            disabled={!row.original.name}
          >
            <Visibility fontSize="small" />
          </button> */}
        </div>
      ),
    },
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
          meta: {
            filterType: "string",
          },
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
    data: logs,
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
    [data.data, logs, data.isFetching, columns]
  );
};
