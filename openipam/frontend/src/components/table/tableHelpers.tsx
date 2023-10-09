import React from "react";
import type { Row, Table } from "@tanstack/react-table";
import { ReactNode, useRef } from "react";
import { DebouncedInput } from "./debouncedInput";
import { IdToName } from "../idToName";
import { Delete, ExpandMore } from "@mui/icons-material";
import { Show } from "../logic";

export const RowsSelected = (p: {
  rows: Row<any>[];
  rowActions: ((any: any) => ReactNode) | undefined;
}) => {
  return (
    <div className="flex flex-col justify-between w-full max-w-2xl">
      {p.rows.length > 0 ? (
        <div className="flex flex-row gap-4 ml-2">
          <p className="">{p.rows.length} Rows Selected</p>
        </div>
      ) : (
        <div className="invisible">No Rows Selected</div>
      )}
      {p.rowActions?.(p.rows.map((r) => r.original))}
    </div>
  );
};

export const ColumnFilters = (p: { table: Table<any> }) => {
  const activeFilters = p.table.getState().columnFilters;

  return (
    <div className="flex flex-row gap-4 m-1">
      <div className="flex flex-col justify-between">
        <div className="flex flex-row gap-4 ">
          {activeFilters.length > 0 && (
            <button
              className="btn btn-sm btn-outline btn-ghost"
              onClick={() => p.table.resetColumnFilters()}
            >
              Clear Filters
            </button>
          )}
        </div>
        <div className="flex gap-2 ">
          <Show
            when={activeFilters.length}
            fallback={<p className="">No Active Column Filters</p>}
          >
            {activeFilters.map((filter) => (
              <div
                className="flex flex-row gap-2 flex-wrap"
                key={Math.random()}
              >
                <p className="">{IdToName(filter.id)}:</p>
                <p className="">{JSON.stringify(filter.value)}</p>
              </div>
            ))}
          </Show>
        </div>
      </div>
    </div>
  );
};

export const AdvancedFilters = (p: { table: Table<any> }) => {
  const [globalFilter, setGlobalFilter] = [
    p.table.getState().globalFilter,
    p.table.setGlobalFilter,
  ];
  return (
    <div className="flex flex-row gap-4 m-1">
      <div className="flex flex-col gap-2 w-full justify-between">
        {globalFilter && <label className=" m-1">Advanced Filters:</label>}
        {globalFilter?.map((filter: { id: string; text: string }) => (
          <div key={Math.random()}>
            <div
              className="flex flex-row justify-between gap-2 flex-wrap card card-bordered p-1 border-neutral-content shadow-neutral"
              key={Math.random()}
            >
              <p className="ml-2 mt-0.5">{filter.text}</p>
              <button
                className="btn btn-sm btn-ghost"
                onClick={() => {
                  setGlobalFilter?.((prev: any[]) =>
                    prev.filter((f) => f.id !== filter.id)
                  );
                }}
              >
                <Delete />
              </button>
            </div>
          </div>
        ))}
        {p.table.options.meta?.globalFilter ?? <></>}
      </div>
    </div>
  );
};

export const PageCounter = (p: { table: Table<any> }) => {
  const rows = p.table.getRowModel().rows;

  const { page, setPage, pageSize } = p.table.options.meta ?? {};
  const total = p.table.options.meta?.total ?? rows.length;

  return (
    <div className="flex flex-row gap-4 m-1 justify-self-end mr-4">
      <div className="flex flex-col justify-between">
        <div className="flex flex-row gap-4">
          <p className="">
            Veiwing {rows.length} of {total} rows
          </p>
        </div>
        {page && setPage && (
          <div className="flex flex-row gap-4">
            <p className="">
              Page {page} of {Math.ceil(total / (pageSize ?? 10))}
            </p>
          </div>
        )}
        {page && setPage && (
          <div className="my-1 flex flex-row gap-1">
            <button
              className="btn btn-ghost btn-outline btn-sm"
              onClick={() => {
                setPage!(page! - 1);
              }}
              disabled={page === 1}
            >
              <ExpandMore style={{ transform: "rotate(90deg)" }} />
            </button>
            <DebouncedInput
              className="input input-primary input-bordered input-sm w-14"
              min={1}
              max={Math.ceil(total / (pageSize ?? 10))}
              value={page}
              onChange={(e) => {}}
              onBlur={(e) => {
                try {
                  const int = parseInt(e.target.value);
                  if (int > Math.ceil(total / (pageSize ?? 10))) {
                    setPage!(Math.ceil(total / (pageSize ?? 10)));
                  } else if (int < 1) {
                    setPage!(1);
                  } else if (isNaN(int)) {
                    setPage!(1);
                  } else setPage!(Number(int));
                } catch {
                  setPage!(1);
                }
              }}
            />
            <button
              className="btn btn-ghost btn-outline btn-sm"
              onClick={() => {
                setPage(page! + 1);
              }}
              disabled={page === Math.ceil(total / (pageSize ?? 10))}
            >
              <ExpandMore style={{ transform: "rotate(-90deg)" }} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
