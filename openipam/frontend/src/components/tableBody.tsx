import { Table, flexRender } from "@tanstack/react-table";
import React from "react";

export const TableBody = (p: {
  table: Table<any>;
  estimateColumnSize?: number;
  tableContainerRef: React.RefObject<HTMLDivElement>;
}) => {
  const tableRows = p.table.getRowModel().rows;

  return (
    <tbody>
      {tableRows.map((virtualRow) => {
        const row = tableRows[virtualRow.index]!;
        return (
          <tr key={row.id}>
            {row.getVisibleCells().map((cell) => (
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
