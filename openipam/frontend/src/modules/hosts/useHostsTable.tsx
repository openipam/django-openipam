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
import { ReactNode, useEffect, useMemo, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { fuzzyFilter } from "../../components/filters";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Host } from "../../utils/types";
import { BooleanRender, booleanAccessor } from "../../components/boolean";
import { ExportToCsv } from "../../components/download";
import { useInfiniteHosts } from "../../hooks/queries/useInfiniteHosts";
import { ActionsColumn } from "../../components/actionsColumn";

//TODO disabled columns only shows for admins.

export const useHostsTable = (p: {
  setShowAddHost: React.Dispatch<React.SetStateAction<boolean>>;
  setEditHost: React.Dispatch<
    React.SetStateAction<{ show: boolean; HostData: Host | undefined }>
  >;
  setRenewModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; data: Host[] | undefined }>
  >;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Host[] | undefined;
      title: string;
      onSubmit?: (data: Host[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
}) => {
  const api = useApi();
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [rowSelection, setRowSelection] = useState({});
  const [columnVisibility, setColumnVisibility] = useState({});
  const [action, setAction] = useState<string>("renew");
  const [prevData, setPrevData] = useState<Host[]>([]);
  const navigate = useNavigate();

  const data = useInfiniteHosts({
    ...Object.fromEntries(
      columnFilters
        .map((filter) => [
          filter.id,
          filter.value as string | number | string[],
        ])
        .map(([key, val]) => {
          switch (key) {
            case "expires":
              return [];
            case "mac":
              return [`mac`, val ?? ""];
            case "hostname":
              return [`hostname`, val ?? ""];
            case "group_owners":
              return [`group`, val ?? ""];
            default:
              return [key, val ?? ""];
          }
        })
    ),
    expires__gt: (columnFilters.find((filter) => filter.id === "expires")
      ?.value as (string | undefined)[])?.[0],
    expires__lt: (columnFilters.find((filter) => filter.id === "expires")
      ?.value as (string | undefined)[])?.[1],
  });

  const Hosts = useMemo<Host[]>(() => {
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

  const columnHelper = createColumnHelper<Host>();
  const columns = [
    ...ActionsColumn({
      data: Hosts,
      enableSelection: true,
      onAdd: () => {
        p.setShowAddHost((prev: boolean) => !prev);
      },
      onEdit: (data) => {
        p.setEditHost({
          show: true,
          HostData: data,
        });
      },
      onView: (data) => {
        navigate(`/Hosts/${data.mac}`);
      },
      onRenew: (data) => {
        p.setRenewModule({
          show: true,
          data: [data],
        });
      },
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "mac",
          header: "Mac",
          accessorFn: (row) => row.mac,
          meta: {
            filterType: "string",
          },
          filterFn: undefined,
        },
        {
          id: "hostname",
          header: "Hostname",
          accessorFn: (row) => row.hostname,
          meta: {
            filterType: "string",
          },
          filterFn: undefined,
        },
      ],
    }),
    columnHelper.group({
      id: "Primary Details",
      header: "Primary Details",
      columns: [
        {
          id: "expires",
          size: 200,
          header: "Expires",
          accessorFn: (row) =>
            row.expires
              ? new Date(row.expires).toISOString().split("T")[0]
              : null,
          cell: ({ row }: { row: any }) => {
            return row?.original.expires ? (
              <div className="flex flex-col">
                <p className="flex flex-row justify-start">{`${
                  row.original.expires
                    ? new Date(row.original.expires).toISOString().split("T")[0]
                    : ""
                }`}</p>
                <p className="flex flex-row justify-end">{`(${
                  new Date(row.original.expires) < new Date()
                    ? "Expired"
                    : `${Math.ceil(
                        (new Date(row.original.expires).getTime() -
                          new Date().getTime()) /
                          (1000 * 3600 * 24)
                      )} Days Left`
                })`}</p>
              </div>
            ) : (
              ""
            );
          },
          meta: {
            filterType: "date",
          },
          filterFn: undefined,
        },
        {
          id: "ip_addresses",
          header: "IP Addresses",
          cell: ({ row }: { row: any }) => {
            return row.original.master_ip_address ||
              row.addresses?.leased?.[0] ? (
              <div className="flex flex-row">
                <a
                  className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                  href={`#/addresses/${
                    row.original.master_ip_address ?? row.addresses?.leased?.[0]
                  }`}
                >{`${
                  row.original.master_ip_address ??
                  row.original.addresses?.leased?.[0]
                }`}</a>
                <p className="flex align-middle m-auto">{`(${
                  row.original.addresses?.leased?.length +
                  row.original.addresses?.static?.length
                })`}</p>
              </div>
            ) : (
              <p className="flex align-middle m-auto">No IP Address</p>
            );
          },
          accessorFn: (row) =>
            row.master_ip_address ?? row.addresses?.leased?.[0],
          meta: {
            filterType: "string",
          },
        },
        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group?.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "disabled_host",
          size: 75,
          header: "Disabled Host",
          accessorFn: booleanAccessor("disabled_host"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_dynamic",
          size: 75,
          header: "Dynamic",
          cell: BooleanRender,
          accessorFn: booleanAccessor("is_dynamic"),
          meta: {
            filterType: "boolean",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Owners",
      header: "Owners",
      columns: [
        {
          id: "user_owners",
          header: "User Owners",
          size: 200,
          accessorFn: (row) => row.user_owners?.join(", "),
          meta: {
            filterType: "string",
          },
        },
        {
          id: "group_owners",
          header: "Group Owners",
          size: 200,
          accessorFn: (row) => row.group_owners?.join(", "),
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
    // Row Selection
    enableRowSelection: true,
    enableMultiRowSelection: true,
    onRowSelectionChange: setRowSelection,
    onColumnVisibilityChange: setColumnVisibility,
    data: Hosts,
    state: {
      columnFilters,
      rowSelection,
      get globalFilter() {
        return globalFilter;
      },
      set globalFilter(value) {
        setGlobalFilter(value);
      },
      columnVisibility,
    },
    meta: {
      trProps: (row: any) => {
        return {
          className:
            row.expires && new Date(row.expires) < new Date()
              ? "bg-red-500 bg-opacity-70"
              : "",
        };
      },
      rowActions: (rows: Host[]) => {
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
                className="rounded-md p-2 select select-bordered max-w-md"
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
                    case "renew":
                      p.setRenewModule({
                        show: true,
                        data: rows,
                      });
                      break;
                    case "disable":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Disable Hosts",
                        onSubmit: (data) => {
                          rows.forEach((host) => {
                            api.hosts.byId(host.mac).disable({
                              reason: data,
                            });
                          });
                        },
                        children: (
                          <div>
                            <label className="label">Reason</label>
                            <input
                              type="test"
                              className="input input-bordered"
                            />
                          </div>
                        ),
                      });
                      break;
                    case "enable":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Enable Hosts",
                        onSubmit: () => {
                          rows.forEach((host) => {
                            api.hosts.byId(host.mac).enable();
                          });
                        },
                        children: (
                          <div>
                            <input className="hidden" />
                          </div>
                        ),
                      });
                      break;
                    case "delete":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Delete Hosts",
                        onSubmit: () => {
                          rows.forEach((host) => {
                            api.hosts.byId(host.mac).delete();
                          });
                        },
                        children: (
                          <div>
                            <input className="hidden" />
                          </div>
                        ),
                      });
                      break;
                    case "rename":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        multiple: true,
                        title: "Rename Hosts",
                        onSubmit: (e: any) => {
                          const regex = e.target[0].value;
                          const replacement = e.target[1].value;
                          rows.forEach((host) => {
                            api.hosts.byId(host.mac).update({
                              hostname: host.hostname.replace(
                                regex,
                                replacement
                              ),
                            });
                          });
                        },
                        children: (
                          <div>
                            <label className="label">Regex</label>
                            <input className="input input-bordered" />
                            <label className="label">Replacement</label>
                            <input className="input input-bordered" />
                          </div>
                        ),
                      });
                      break;
                    case "export":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Download CSV",
                        children: (
                          <div className="m-auto mt-10">
                            <ExportToCsv
                              rows={rows}
                              columns={table
                                .getAllLeafColumns()
                                .slice(1)
                                .map((col) => col.columnDef)}
                              fileName="Hosts"
                            />
                          </div>
                        ),
                      });
                      break;
                    case "populate":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Populate DNS Records",
                        onSubmit: () => {
                          rows.forEach((host) => {
                            api.hosts.byId(host.mac).populateDns();
                          });
                        },
                        children: (
                          <div>
                            <input className="hidden" />
                          </div>
                        ),
                      });
                      break;
                    case "changeNetwork":
                      break;
                    case "addOwners":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Add Owners",
                        multiple: true,
                        onSubmit: (e: any) => {
                          const group = e.target[0].value.split(",");
                          const users = e.target[1].value.split(",");
                          rows.forEach((host) => {
                            api.hosts
                              .byId(host.mac)
                              .users.create(
                                Object.fromEntries(
                                  users.map((user: string) => [user, user])
                                )
                              );
                            api.hosts
                              .byId(host.mac)
                              .groups.create(
                                Object.fromEntries(
                                  group.map((group: string) => [group, group])
                                )
                              );
                          });
                        },
                        children: (
                          <div>
                            <p>
                              Tip: add multiple owners by separating with a
                              comma
                            </p>
                            <label className="label">Group Owners</label>
                            <input className="input input-bordered" />
                            <label className="label">User Owners</label>
                            <input className="input input-bordered" />
                          </div>
                        ),
                      });
                      break;
                    case "replaceOwners":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Replace Owners",
                        multiple: true,
                        onSubmit: (e: any) => {
                          const group = e.target[0].value.split(",");
                          const users = e.target[1].value.split(",");
                          rows.forEach((host) => {
                            api.hosts
                              .byId(host.mac)
                              .users.put(
                                Object.fromEntries(
                                  users.map((user: string) => [user, user])
                                )
                              );
                            api.hosts
                              .byId(host.mac)
                              .groups.put(
                                Object.fromEntries(
                                  group.map((group: string) => [group, group])
                                )
                              );
                          });
                        },
                        children: (
                          <div>
                            <p>
                              Tip: separate owners by comma. All previous owners
                              will be removed.
                            </p>
                            <label className="label">Group Owners</label>
                            <input className="input input-bordered" />
                            <label className="label">User Owners</label>
                            <input className="input input-bordered" />
                          </div>
                        ),
                      });
                      break;
                    case "removeOwners":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Remove Owners",
                        multiple: true,
                        onSubmit: (e: any) => {
                          const group = e.target[0].value.split(",");
                          const users = e.target[1].value.split(",");
                          rows.forEach((host) => {
                            api.hosts
                              .byId(host.mac)
                              .users.put(
                                Object.fromEntries(
                                  host.user_owners
                                    .filter((u) => !users.includes(u))
                                    .map((user: string) => [user, user])
                                )
                              );
                            api.hosts
                              .byId(host.mac)
                              .groups.put(
                                Object.fromEntries(
                                  host.group_owners
                                    .filter((u) => !group.includes(u))
                                    .map((group: string) => [group, group])
                                )
                              );
                          });
                        },
                        children: (
                          <div>
                            <p>
                              Tip: remove multiple owners by separating with a
                              comma
                            </p>
                            <label className="label">Group Owners</label>
                            <input className="input input-bordered" />
                            <label className="label">User Owners</label>
                            <input className="input input-bordered" />
                          </div>
                        ),
                      });
                      break;
                    case "addAttribute":
                      break;
                    case "deleteAttribute":
                      break;
                    case "setDhcpGroup":
                      break;
                    case "deleteDhcpGroup":
                      break;
                    default:
                      break;
                  }
                }}
              >
                Go
              </button>
            </div>
          </div>
        );
      },
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

const actions = {
  renew: "Renew",
  disable: "Disable",
  enable: "Enable",
  delete: "Delete",
  rename: "Rename",
  export: "Export to CSV",
  populate: "Populate DNS",
  changeNetwork: "Change Network",
  addOwners: "Add Owners",
  replaceOwners: "Replace Owners",
  removeOwners: "Remove Owners",
  addAttribute: "Add Attribute",
  deleteAttribute: "Delete Attribute",
  setDhcpGroup: "Set DHCP Group",
  deleteDhcpGroup: "Delete DHCP Group",
};
