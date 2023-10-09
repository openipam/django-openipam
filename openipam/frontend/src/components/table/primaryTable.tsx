import React from "react";
import { TableBody } from "./tableBody";
import { TableHead, TableHeaderCell } from "./tableHead";
import { useAuth } from "../../hooks/useAuth";
import type { Table } from "@tanstack/react-table";
import { useRef } from "react";
import { Show } from "../logic";
import {
  AdvancedFilters,
  ColumnFilters,
  PageCounter,
  RowsSelected,
} from "./tableHelpers";

export const PrimaryTable = (p: {
  estimateColumnSize?: number;
  table: Table<any>;
  className?: string;
}) => {
  const auth = useAuth();
  const tableContainerRef = useRef<HTMLDivElement>(null);

  return (
    <div>
      <div className="w-full grid grid-cols-4 gap-10">
        <Show when={auth?.is_ipamadmin}>
          <RowsSelected
            rows={p.table.getSelectedRowModel().rows}
            rowActions={p.table.options.meta?.rowActions}
          />
        </Show>
        <ColumnFilters table={p.table} />
        <AdvancedFilters table={p.table} />
        <PageCounter table={p.table} />
      </div>
      <div
        ref={tableContainerRef}
        className={`overflow-scroll
       max-h-[calc(100vh-102px)] ${p.className}`}
      >
        <table className={`table table-sm table-fixed `}>
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
                    footer
                  />
                ))}
              </tr>
            ))}
          </tfoot>
        </table>
      </div>
    </div>
  );
};
