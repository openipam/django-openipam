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
    filterOptions?: string[] | null;
    filterType?: "string" | "date" | "exact" | "boolean" | null;
    hideFilter?: boolean;
  }

  interface TableMeta<TData extends RowData> {
    trProps?: (p: TData) => Record<string, any>;
    rowActions?: (p: TData) => React.ReactNode;
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
    <div className="flex flex-col overflow-scroll gap-4 m-8 w-[90%]">
      <div className="flex relative mb-2 p-2">
        {p.loading ? (
          <div className="text-secondary-content absolute">
            <p className="text-secondary-content">Syncing...</p>
          </div>
        ) : (
          <div></div>
        )}
      </div>
      <PrimaryTable
        table={p.table}
        estimateColumnSize={p.estimateColumnSize}
        className={p.className}
      />
    </div>
  );
};
