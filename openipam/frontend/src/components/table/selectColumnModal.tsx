import React from "react";
import { useId } from "react";

import { Column, Table as ReactTable, flexRender } from "@tanstack/react-table";
import { IdToName } from "../idToName";

export const SelectColumnModal = (p: {
  table: ReactTable<any>;
  showSelectColumns: boolean;
  hideShowSelectColumns: VoidFunction;
}) => {
  const selectColumnsModalId = useId();

  const leafCols = p.table.getAllLeafColumns();

  const grouped = leafCols.reduce<
    Map<string | undefined, Column<any, unknown>[]>
  >((map, next) => {
    const p = map.get(next.parent?.id as string | undefined) ?? [];
    if (next.getCanHide()) {
      p.push(next);
      map.set(next.parent?.id, p);
    }
    return map;
  }, new Map());
  return (
    <>
      <input
        type="checkbox"
        id={selectColumnsModalId}
        className="modal-toggle"
        checked={p.showSelectColumns ?? false}
        readOnly
      />
      <div className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-2xl">Select columns to display</h3>
          <div className="flex gap-2 flex-wrap mt-3">
            {[...grouped.entries()].map(([label, cols]) => {
              return (
                <div key={label}>
                  <h3 className="text-xl mb-2">{label ?? ""}</h3>
                  <div className="flex flex-col gap-1">
                    {cols.map((column) => (
                      <label
                        key={column.id}
                        className="cursor-pointer flex flex-row gap-2 items-center"
                      >
                        <input
                          type="checkbox"
                          className="checkbox"
                          checked={column.getIsVisible()}
                          onChange={column.getToggleVisibilityHandler()}
                        />
                        <span>{IdToName(column.columnDef.id ?? "")}</span>
                      </label>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="modal-action">
            <button onClick={p.hideShowSelectColumns} className="btn">
              Done
            </button>
          </div>
        </div>
      </div>
    </>
  );
};
