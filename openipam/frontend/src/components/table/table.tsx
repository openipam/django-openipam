import "@tanstack/react-table";
import type { Table as ReactTable, RowData } from "@tanstack/react-table";
import type { Component, ReactNode } from "react";
import { PrimaryTable } from "./primaryTable";
import React from "react";
import { SelectColumnModal } from "./selectColumnModal";

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
    total?: number;
    pageSize?: number;
    globalFilter?: ReactNode;
    page?: number;
    setPage?: React.Dispatch<React.SetStateAction<number>>;
  }
}

export const Table = (
  p: {
    estimateColumnSize?: number;
    table: ReactTable<any>;
    loading: boolean;
    className?: string;
  } & (
    | {
        showSelectColumns: boolean;
        hideShowSelectColumns: VoidFunction;
      }
    | {
        showSelectColumns?: never;
        hideShowSelectColumns?: never;
      }
  )
) => {
  return (
    <div className="flex flex-col gap-4 mx-8 w-[90%]">
      {p.hideShowSelectColumns ? <SelectColumnModal {...p} /> : null}
      <div className="flex relative mb-2 p-2">
        {p.loading ? (
          <div className=" absolute">
            <p className="">Syncing...</p>
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
