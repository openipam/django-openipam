import type { Table } from "@tanstack/react-table";
import { useRef } from "react";
import { DebouncedInput } from "./debouncedInput";
import { TableBody } from "./tableBody";
import { TableHead, TableHeaderCell } from "./tableHead";
import React from "react";

export const PrimaryTable = (p: {
  estimateColumnSize?: number;
  table: Table<any>;
  hideGlobalFilter?: boolean;
  className?: string;
}) => {
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const [globalFilter, setGlobalFilter] = [
    p.table.getState().globalFilter,
    p.table.setGlobalFilter,
  ];
  const selectedRows = p.table.getSelectedRowModel();

  return (
    <div
      ref={tableContainerRef}
      className={`overflow-scroll max-h-[calc(100vh-192px)] ${
        p.className || ""
      }`}
    >
      {selectedRows?.rows?.length > 0 && (
        <div className="flex flex-col justify-between">
          <div className="flex gap-4 text-white">
            <p className="text-white">
              {selectedRows.rows.length} Rows Selected
            </p>
          </div>
          {p.table.options.meta?.rowActions?.(
            selectedRows.rows.map((r) => r.original)
          )}
        </div>
      )}
      {!p.hideGlobalFilter && (
        <div>
          <DebouncedInput
            value={globalFilter ?? ""}
            onChange={(value) => setGlobalFilter(String(value))}
            className="mb-2 input input-bordered w-full"
            placeholder="Search any column..."
          />
        </div>
      )}
      <table className="table table-sm table-fixed">
        <TableHead table={p.table} />
        <TableBody
          tableContainerRef={tableContainerRef}
          table={p.table}
          estimateColumnSize={p.estimateColumnSize}
        />
        <tfoot>
          {p.table.getFooterGroups().map((footerGroups) => (
            <tr key={footerGroups.id} className="sticky bottom-0">
              {footerGroups.headers.map((header) => (
                <TableHeaderCell
                  header={header}
                  headerGroup={footerGroups}
                  key={header.id}
                  hideSorting
                  hideFilter
                  table={p.table}
                />
              ))}
            </tr>
          ))}
        </tfoot>
      </table>
    </div>
  );
};
