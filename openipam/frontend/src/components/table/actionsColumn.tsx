import React, { ReactNode } from "react";
import { PlainIndeterminateCheckbox } from "./boolean";
import {
  Add,
  Autorenew,
  Edit,
  ExpandMore,
  Visibility,
} from "@mui/icons-material";
import { ToolTip } from "../tooltip";

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
      header: ({ table }: any) => (
        // force overflow to be visible so that the tooltip can be seen
        <div className="flex gap-1 items-center relative">
          {p.enableSelection && (
            <PlainIndeterminateCheckbox
              checked={table.getIsAllRowsSelected()}
              indeterminate={table.getIsSomeRowsSelected()}
              onChange={table.getToggleAllRowsSelectedHandler()}
            />
          )}
          <ToolTip text="Load More" props="bottom-8 left-0 rounded-bl-none">
            <button
              className="btn btn-circle btn-ghost btn-xs mt-1"
              onClick={() => p.data.fetchNextPage?.()}
              disabled={!p.data.hasNextPage || p.data.isFetchingNextPage}
            >
              <ExpandMore />
            </button>
          </ToolTip>
          {p.onAdd && (
            <button
              className="btn btn-circle btn-ghost btn-xs"
              onClick={p.onAdd}
            >
              <Add />
            </button>
          )}
          {p.customHead}
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
