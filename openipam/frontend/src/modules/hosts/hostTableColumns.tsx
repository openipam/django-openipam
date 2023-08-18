import { createColumnHelper } from "@tanstack/react-table";
import React, { ReactNode } from "react";
import { Host, User } from "../../utils/types";
import { ActionsColumn } from "../../components/actionsColumn";
import { useNavigate } from "react-router-dom";
import { BooleanRender, booleanAccessor } from "../../components/boolean";
import { UseInfiniteQueryResult } from "@tanstack/react-query";

export const HostTableColumns = (p: {
  data: UseInfiniteQueryResult<
    {
      results: any;
      page: any;
      nextPage: any;
    },
    unknown
  >;
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
  auth: User | undefined;
}) => {
  const columnHelper = createColumnHelper<Host>();
  const navigate = useNavigate();
  return [
    ...(p.auth?.is_ipamadmin
      ? ActionsColumn({
          data: p.data,
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
        })
      : ActionsColumn({
          size: 80,
          data: p.data,
          onView: (data) => {
            navigate(`/Hosts/${data.mac}`);
          },
        })),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "mac",
          header: "Mac",
          accessorFn: (row) => row.mac,
        },
        {
          id: "hostname",
          header: "Hostname",
          accessorFn: (row) => row.hostname,
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
        },
        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group?.name,
        },
        {
          id: "is_dynamic",
          size: 80,
          header: "Dynamic",
          cell: BooleanRender,
          // accessorFn: booleanAccessor("is_dynamic"),
          // meta: {
          //   filterType: "boolean",
          // },
        },
      ],
    }),
    p.auth?.is_staff
      ? columnHelper.group({
          id: "Secondary Details",
          header: "Secondary Details",
          columns: [
            {
              id: "disabled_host",
              size: 80,
              header: "Disabled",
              accessorFn: booleanAccessor("disabled_host"),
              cell: BooleanRender,
              meta: {
                filterType: "boolean",
              },
              filterFn: undefined,
            },
            {
              id: "user_owners",
              header: "User Owners",
              size: 200,
              accessorFn: (row) => row.user_owners?.join(", "),
            },
            {
              id: "group_owners",
              header: "Group Owners",
              size: 200,
              accessorFn: (row) => row.group_owners?.join(", "),
            },
          ],
        })
      : columnHelper.group({
          id: "Owners",
          header: "Owners",
          columns: [
            {
              id: "user_owners",
              header: "User Owners",
              size: 200,
              accessorFn: (row) => row.user_owners?.join(", "),
            },
            {
              id: "group_owners",
              header: "Group Owners",
              size: 200,
              accessorFn: (row) => row.group_owners?.join(", "),
            },
          ],
        }),
  ];
};
