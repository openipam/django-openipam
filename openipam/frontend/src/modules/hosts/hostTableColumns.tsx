import { createColumnHelper } from "@tanstack/react-table";
import React, { ReactNode } from "react";
import { Host, User } from "../../utils/types";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { useNavigate } from "react-router-dom";
import { UseInfiniteQueryResult } from "@tanstack/react-query";
import { ToolTip } from "../../components/tooltip";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { MoreVert } from "@mui/icons-material";

export const HostTableColumns = (p: {
  data: UseInfiniteQueryResult<
    {
      results: any;
      page: any;
      nextPage: any;
      count: number;
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
  pageSize: number;
  setPageSize: React.Dispatch<React.SetStateAction<number>>;
  setSelectAll: React.Dispatch<React.SetStateAction<boolean>>;
  auth: User | undefined;
}) => {
  const columnHelper = createColumnHelper<Host>();
  const addressTypes = useAddressTypes().data?.addressTypes;
  const navigate = useNavigate();
  return [
    ...(p.auth?.is_ipamadmin
      ? ActionsColumn({
          size: 150,
          data: p.data,
          pageSize: p.pageSize,
          setPageSize: p.setPageSize,
          setSelectAll: p.setSelectAll,
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
          customHead: (
            <>
              <div className="dropdown mt-1">
                <label tabIndex={0} className="btn btn-circle btn-ghost btn-xs">
                  <MoreVert />
                </label>
                <ul
                  tabIndex={0}
                  className="dropdown-content menu p-2 shadow bg-gray-700 rounded-box w-40 mt-2"
                >
                  <li
                    onClick={() => {
                      p.setSelectAll(true);
                    }}
                  >
                    <ToolTip
                      text="Caution! Includes Unseen Rows!"
                      props="rounded-tr-none top-10 right-2"
                    >
                      <a>Select ALL rows</a>
                    </ToolTip>
                  </li>
                </ul>
              </div>
            </>
          ),
        })
      : ActionsColumn({
          size: 100,
          data: p.data,
          pageSize: p.pageSize,
          setPageSize: p.setPageSize,
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
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-secondary-content">Mac</p>
              <ToolTip
                text="Use XX:XX:XX:XX:XX:XX Format"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
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
          size: 120,
          header: "Expires",
          accessorFn: (row) =>
            row.expires
              ? new Date(row.expires).toISOString().split("T")[0]
              : null,
          cell: ({ row }: { row: any }) => {
            return row?.original.expires ? (
              <div className="flex flex-row flex-wrap justify-around">
                {/* <p className="flex flex-row justify-start">{`${
                  row.original.expires
                    ? new Date(row.original.expires).toISOString().split("T")[0]
                    : ""
                }`}</p> */}
                <p className="flex flex-row justify-center">{`${
                  new Date(row.original.expires) < new Date()
                    ? "Expired"
                    : `${Math.ceil(
                        (new Date(row.original.expires).getTime() -
                          new Date().getTime()) /
                          (1000 * 3600 * 24)
                      )} Days Left`
                }`}</p>
              </div>
            ) : (
              ""
            );
          },
          meta: {
            filterType: "exact",
            filterOptions: expiredFilterOptions.map((t) => t),
          },
        },
        {
          id: "ip_addresses",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-secondary-content">
                IP Addresses
              </p>
              <ToolTip
                text="XX.XX.XX.XX"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
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
          filterFn: undefined,
        },
      ],
    }),
    columnHelper.group({
      id: "Secondary Details",
      header: "Secondary Details",
      columns: [
        {
          id: "address_type",
          header: "Address Type",
          accessorFn: (row) => row.address_type,
          meta: {
            filterType: "exact",
            filterOptions: addressTypes?.map((t) => t.name) ?? [],
          },
        },
        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group?.name,
        },
      ],
    }),
    columnHelper.group({
      id: "Owners",
      header: "Owners",
      columns: [
        {
          id: "user_owners",
          // header: "User Owners",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-secondary-content">
                User Owners
              </p>
              <ToolTip
                text="By Username"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
          size: 200,
          accessorFn: (row) => row.user_owners?.join(", "),
        },
        {
          id: "group_owners",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-secondary-content">
                Group Owners
              </p>
              <ToolTip
                text="Use Full Name"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
          size: 200,
          accessorFn: (row) => row.group_owners?.join(", "),
        },
      ],
    }),
  ];
};

export const expiredFilterOptions = [
  "Expired",
  "1 Day Left",
  "7 Days Left",
  "30 Days Left",
  "Unexpired",
] as const;
