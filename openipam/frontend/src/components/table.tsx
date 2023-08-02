import "@tanstack/react-table";
import type { Table as ReactTable, RowData } from "@tanstack/react-table";
import type { Component } from "react";
import { PrimaryTable } from "./primaryTable";
import React from "react";

declare module "@tanstack/table-core" {
  interface ColumnMeta<TData extends RowData, TValue> {
    tdProps?: (
      p: TData
    ) => Record<string, any> & {
      className?: Component<HTMLTableCellElement>["props"]["className"];
    };
    thProps?: () => Record<string, any> & {
      className?: Component<HTMLTableCellElement>["props"]["className"];
    };
    filterOptions?:
      | {
          label: string;
          value: string | number;
        }[]
      | null;
    filterType: "string" | "date" | null;
  }
}

export const Table = (p: {
  estimateColumnSize?: number;
  table: ReactTable<any>;
  loading: boolean;
  hideGlobalFilter?: boolean;
  className?: string;
}) => {
  return (
    <div>
      <div className="flex justify-between items-center">
        {p.loading ? (
          <div className="flex gap-4 text-white">
            <p className="text-white">Syncing...</p>
          </div>
        ) : (
          <div></div>
        )}
      </div>
      <PrimaryTable
        table={p.table}
        estimateColumnSize={p.estimateColumnSize}
        hideGlobalFilter={p.hideGlobalFilter}
        className={p.className}
      />
    </div>
  );
};