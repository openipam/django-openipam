import type { Row, RowSelectionState, Table } from "@tanstack/react-table";
import { useRef } from "react";
import { DebouncedInput } from "./debouncedInput";
import { TableBody } from "./tableBody";
import { TableHead, TableHeaderCell } from "./tableHead";
import React from "react";
import { useAuth } from "../../hooks/useAuth";
import { IdToName } from "../idToName";
import { Delete, ExpandMore } from "@mui/icons-material";
import { ToolTip } from "../tooltip";
import { parse } from "path";

export const PrimaryTable = (p: {
  estimateColumnSize?: number;
  table: Table<any>;
  className?: string;
}) => {
  const auth = useAuth();
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const selectedRows = p.table.getSelectedRowModel();
  const activeFilters = p.table.getState().columnFilters;
  const rows = p.table.getRowModel().rows;
  const total = p.table.options.meta?.total ?? rows.length;
  const [globalFilter, setGlobalFilter] = [
    p.table.getState().globalFilter,
    p.table.setGlobalFilter,
  ];
  const { page, setPage, pageSize } = p.table.options.meta ?? {};

  return (
    <div
      ref={tableContainerRef}
      className={`overflow-scroll max-h-[calc(100vh-102px)] ${
        p.className || ""
      }`}
    >
      <div className="w-full grid grid-cols-4 gap-10">
        {auth?.is_ipamadmin ? (
          <div className="flex flex-col justify-between w-full max-w-2xl">
            {selectedRows.rows.length > 0 ? (
              <div className="flex flex-row gap-4 ml-2">
                <p className="">{selectedRows.rows.length} Rows Selected</p>
              </div>
            ) : (
              <div className="invisible">No Rows Selected</div>
            )}
            {p.table.options.meta?.rowActions?.(
              selectedRows.rows.map((r) => r.original)
            )}
          </div>
        ) : (
          <div></div>
        )}

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
              {activeFilters.length ? (
                activeFilters.map((filter) => (
                  <div
                    className="flex flex-row gap-2 flex-wrap"
                    key={Math.random()}
                  >
                    <p className="">{IdToName(filter.id)}:</p>
                    <p className="">{JSON.stringify(filter.value)}</p>
                  </div>
                ))
              ) : (
                <p className="">No Active Column Filters</p>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-row gap-4 m-1">
          <div className="flex flex-col gap-2 w-full justify-between">
            {globalFilter && <label className=" m-1">Advanced Filters:</label>}
            {globalFilter?.map((filter: { id: string; text: string }) => (
              <>
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
              </>
            ))}
            {p.table.options.meta?.globalFilter ?? <></>}
          </div>
        </div>
        <div className="flex flex-row gap-4 m-1 justify-self-end mr-4">
          <div className="flex flex-col justify-between">
            <div className="flex flex-row gap-4">
              <p className="">
                Loaded {rows.length} of {total} rows
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
      </div>
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
                  footer
                />
              ))}
            </tr>
          ))}
        </tfoot>
      </table>
    </div>
  );
};
