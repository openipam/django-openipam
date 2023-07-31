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
import { useApi } from "../../hooks/useApi";
import { fuzzyFilter } from "../../components/filters";
import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";

type Domain = {
  id: number;
  name: string;
  description: string;
  changed_by: string;
  master: string;
  last_check: string;
  type: string;
  notified_serial: string;
  account: string;
  changed: string;
};

export const useInfiniteDomains = () => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["domains, all"],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.domains.get({ page: pageParam });
      return { results: results.results, page: pageParam };
    },
    getNextPageParam: (lastPage) => {
      return lastPage.results.length > 0 ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 0;
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 10) {
      query.fetchNextPage();
    }
  }, [
    query.hasNextPage,
    query.isFetchingNextPage,
    query.fetchNextPage,
    query.data,
  ]);
  return query;
};

export const useDomainsTable = () => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Domain[]>([]);

  const data = useInfiniteDomains();
  console.log(data);
  const domains = useMemo<Domain[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);
  console.log(domains);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.results)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<Domain>();
  const columns = [
    //   {
    //     size: 100,
    //     enableHiding: false,
    //     enableSorting: false,
    //     enableColumnFilter: false,
    //     id: "actions",
    //     header: ({ table }) => (
    //       <div className="flex gap-1 items-center">
    //         <PlainIndeterminateCheckbox
    //           checked={table.getIsAllRowsSelected()}
    //           indeterminate={table.getIsSomeRowsSelected()}
    //           onChange={table.getToggleAllRowsSelectedHandler()}
    //         />
    //         <div className="tooltip tooltip-right" data-tip="Load More">
    //           <button
    //             className="btn btn-circle btn-ghost btn-xs mt-1"
    //             onClick={() => data.fetchNextPage?.()}
    //             disabled={!data.hasNextPage || data.isFetchingNextPage}
    //           >
    //             <ExpandMore />
    //           </button>
    //         </div>
    //         <div className="dropdown mt-1">
    //           <label tabIndex={0} className="btn btn-circle btn-ghost btn-xs">
    //             <MoreVert />
    //           </label>
    //           <ul
    //             tabIndex={0}
    //             className="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52"
    //           >
    //             <li onClick={p.onSelectColumns}>
    //               <a>Show/Hide Columns</a>
    //             </li>
    //           </ul>
    //         </div>
    //         {/* <button
    //                 className="btn btn-circle btn-ghost btn-xs"
    //                 onClick={p.onAdd}
    //                 disabled
    //                 >
    //                 <Add />
    //                 </button> */}
    //       </div>
    //     ),
    //     cell: ({ row }) => (
    //       <div className="flex gap-1 items-center">
    //         <PlainIndeterminateCheckbox
    //           checked={row.getIsSelected()}
    //           onChange={row.getToggleSelectedHandler()}
    //           disabled={!row.getCanSelect()}
    //           indeterminate={row.getIsSomeSelected()}
    //         />
    //         <button
    //           className="btn btn-circle btn-ghost btn-xs"
    //           // onClick={() => p.onView(row.original.purchaseOrderId)}
    //           disabled={!row.original.jobId}
    //         >
    //           <Visibility fontSize="small" />
    //         </button>
    //         {/* <button
    //                 className="btn btn-circle btn-ghost btn-xs"
    //                 onClick={() => p.onEdit(row.original.customerId)}
    //                 >
    //                 <Edit fontSize="small" />
    //                 </button> */}
    //       </div>
    //     ),
    //   },
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "id",
          header: "Id",
          accessorFn: (row) => row.id,
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
          id: "type",
          header: "Type",
          accessorFn: (row) => row.type,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
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
          id: "master",
          header: "Master",
          accessorFn: (row) => row.master,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "changed",
          header: "Last Changed",
          accessorFn: (row) => row.changed,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "changedBy",
          header: "Changed By",
          accessorFn: (row) => row.changed_by,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "last_check",
          header: "Last Check",
          accessorFn: (row) => row.last_check,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "notified_serial",
          header: "Notified Serial",
          accessorFn: (row) => row.notified_serial,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "account",
          header: "Account",
          accessorFn: (row) => row.account,
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
    data: domains,
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

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};
