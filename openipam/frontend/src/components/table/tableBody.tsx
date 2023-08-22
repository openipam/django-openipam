import { Table, flexRender } from "@tanstack/react-table";
import React from "react";

export const TableBody = (p: {
  table: Table<any>;
  estimateColumnSize?: number;
  tableContainerRef: React.RefObject<HTMLDivElement>;
}) => {
  const tableRows = p.table.getRowModel().rows ?? [];
  if (!tableRows.length) {
    return (
      <tbody>
        <tr>
          <td className="overflow-hidden" colSpan={2}>
            <div className="flex justify-center items-center h-32">
              <div className="text-2xl">No Results</div>
            </div>
          </td>
        </tr>
      </tbody>
    );
  }

  return (
    <tbody>
      {tableRows.map((row) => {
        return (
          <tr
            key={row.id}
            {...(p.table.options.meta?.trProps?.(row.original) ?? {})}
          >
            {row.getVisibleCells().map((cell, i) => (
              <td
                className="overflow-hidden"
                key={cell.id}
                {...(cell.column.columnDef.meta?.tdProps?.(row.original) ?? {})}
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        );
      })}
    </tbody>
  );
};
