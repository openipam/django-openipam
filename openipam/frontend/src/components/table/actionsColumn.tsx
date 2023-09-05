import React, { ReactNode } from "react";
import { PlainIndeterminateCheckbox } from "./boolean";
import {
  Add,
  Autorenew,
  Edit,
  ExpandMore,
  MoreVert,
  Visibility,
} from "@mui/icons-material";
import { ToolTip } from "../tooltip";
import { Table } from "@tanstack/table-core";
const pageSizes = [10, 25, 50, 100, 200];

export const ActionsColumn = (p: {
  size?: number;
  data: any;
  enableSelection?: boolean;
  onAdd?: () => void;
  onView?: (row: any) => void;
  onEdit?: (row: any) => void;
  onRenew?: (row: any) => void;
  customHead?: ReactNode;
  customCell?: ReactNode;
  pageSize?: number;
  setPageSize?: React.Dispatch<React.SetStateAction<number>>;
  setSelectAll?: React.Dispatch<React.SetStateAction<boolean>>;
  onSelectColumns?: () => void;
}) => {
  return [
    {
      size: p.size ?? 125,
      enableHiding: false,
      enableSorting: false,
      enableResizing: false,
      enableColumnFilter: false,
      accessorFn: () => null,
      meta: {
        hideFilter: true,
      },
      id: "actions",
      header: ({ table }: { table: Table<any> }) => (
        // force overflow to be visible so that the tooltip can be seen
        <div className="flex flex-col gap-1">
          <div className="flex gap-1 relative">
            {p.pageSize && p.setPageSize && (
              <>
                <ToolTip
                  text="Page Size"
                  props="bottom-8 right-1 rounded-br-none"
                >
                  <select
                    className="select select-ghost select-sm text-neutral"
                    value={p.pageSize}
                    onChange={(e) => {
                      p.setPageSize!(Number(e.target.value));
                    }}
                  >
                    {pageSizes.map((size) => (
                      <option key={size} value={size}>
                        {size}
                      </option>
                    ))}
                  </select>
                </ToolTip>
              </>
            )}
          </div>

          <div className="flex gap-1 items-center relative text-neutral">
            {p.enableSelection && (
              <PlainIndeterminateCheckbox
                checked={
                  table.getRowModel().rows.filter((row) => row.getIsSelected())
                    .length === table.getRowModel().rows.length ||
                  table.getRowModel().rows.filter((row) => row.getIsSelected())
                    .length === p.pageSize
                }
                indeterminate={table.getIsSomeRowsSelected()}
                header
                onChange={(e) => {
                  p.setSelectAll?.(false);
                  if (!e.target.checked) {
                    table.resetRowSelection(true);
                  } else {
                    const array = Array.from(
                      p.pageSize
                        ? table.getRowModel().rows.slice(0, p.pageSize)
                        : table.getRowModel().rows
                    );
                    table.setRowSelection(
                      Object.fromEntries(array.map((row) => [row.id, true]))
                    );
                  }
                }}
              />
            )}
            {p.onAdd && (
              <button
                className="btn btn-circle btn-ghost btn-xs text-neutral"
                onClick={p.onAdd}
              >
                <Add style={{ fill: "inherit" }} />
              </button>
            )}
            {p.onSelectColumns && (
              <div className="dropdown mt-1">
                <label
                  tabIndex={0}
                  className="btn btn-circle btn-ghost btn-xs text-neutral"
                >
                  <MoreVert style={{ fill: "inherit" }} />
                </label>
                <ul
                  tabIndex={0}
                  className="dropdown-content menu p-2 shadow bg-neutral-focus rounded-box w-48 mt-2"
                >
                  <li onClick={p.onSelectColumns}>
                    <a className="text-neutral-content">Show/Hide Columns</a>
                  </li>
                </ul>
              </div>
            )}

            {p.customHead}
          </div>
        </div>
      ),
      cell: ({ row }: { row: any }) => (
        <div className="gap-1 items-center !min-w-full">
          {p.enableSelection && (
            <PlainIndeterminateCheckbox
              checked={row.getIsSelected()}
              onChange={row.getToggleSelectedHandler()}
              disabled={!row.getCanSelect()}
              indeterminate={row.getIsSomeSelected()}
            />
          )}
          {p.onView && (
            <button
              className="btn btn-circle btn-ghost btn-xs ml-1"
              onClick={() => p.onView?.(row.original)}
            >
              <Visibility fontSize="small" />
            </button>
          )}
          {p.onEdit && (
            <button
              className="btn btn-circle btn-ghost btn-xs"
              onClick={() => {
                p.onEdit?.(row.original);
              }}
            >
              <Edit fontSize="small" />
            </button>
          )}
          {p.onRenew && (
            <button
              className="btn btn-circle btn-ghost btn-xs"
              onClick={() => {
                p.onRenew?.(row.original);
              }}
            >
              <Autorenew fontSize="small" />
            </button>
          )}
          {p.customCell}
        </div>
      ),
    },
  ];
};
