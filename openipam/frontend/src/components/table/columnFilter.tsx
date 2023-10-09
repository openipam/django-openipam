import { Column, Header, Table } from "@tanstack/react-table";
import React from "react";
import { DebouncedInput } from "./debouncedInput";
import { PlainIndeterminateCheckbox } from "./boolean";

export function ColumnFilter({
  column,
  table,
  header,
}: {
  column: Column<any, unknown>;
  table: Table<any>;
  header: Header<any, unknown>;
}) {
  const columnFilterValue = column.getFilterValue();

  const filterType = header.column.columnDef.meta?.filterType ?? "string";
  const setPage = table.options.meta?.setPage;
  switch (filterType) {
    case "string":
      return (
        <>
          <DebouncedInput
            type="text"
            value={(columnFilterValue ?? "") as string}
            onChange={(value) => {
              setPage && setPage(1);
              column.setFilterValue(value);
            }}
            placeholder={`Search`}
            className="w-full border  shadow rounded input input-xs input-bordered"
            list={column.id + "list"}
          />
          <div className="h-1" />
        </>
      );
    case "exact":
      const uniqueValues = header.column.columnDef.meta?.filterOptions ?? [];
      return (
        <>
          <datalist id={column.id + "list"}>
            {uniqueValues.map((value: any, i: number) => (
              <option value={value} key={i} />
            ))}
          </datalist>
          <DebouncedInput
            type="text"
            value={(columnFilterValue ?? "") as string}
            onChange={(value) => {
              setPage && setPage(1);
              column.setFilterValue(value);
            }}
            placeholder={`Search (${uniqueValues.length})`}
            className="w-full border  shadow rounded input input-xs input-bordered"
            list={column.id + "list"}
          />
          <div className="h-1" />
        </>
      );
    case "boolean":
      const value = (header.column.getFilterValue() ?? "") as "Y" | "N" | "";
      return (
        <div className="bg-neutral-content text-neutral">
          <PlainIndeterminateCheckbox
            indeterminate={value === "N"}
            checked={value === "Y"}
            header
            onChange={() => {
              setPage && setPage(1);
              header.column.setFilterValue((v: "Y" | "" | "N" | undefined) => {
                if (v === "" || v === undefined) return "Y";
                if (v === "Y") return "N";
                return "";
              });
            }}
          />
        </div>
      );
    case "date":
      const maxDate = new Date().getTime();
      const minDate = new Date("1970-01-01").getTime();
      return (
        <div>
          <div className="flex flex-col w-full space-x-2">
            <input
              type="date"
              min={minDate}
              max={maxDate}
              value={(columnFilterValue as [string, string])?.[0] ?? ""}
              onChange={(e) => {
                setPage && setPage(1);
                column.setFilterValue((old: [string, string]) => [
                  e.target.value,
                  old?.[1],
                ]);
              }}
              placeholder="Search"
              className="border shadow rounded w-full input input-xs input-bordered"
            />
            <input
              type="date"
              min={minDate}
              max={maxDate}
              value={(columnFilterValue as [string, string])?.[1] ?? ""}
              onChange={(e) => {
                setPage && setPage(1);
                column.setFilterValue((old: [string, string]) => [
                  old?.[0],
                  e.target.value,
                ]);
              }}
              placeholder="Search"
              className="border shadow rounded w-full input input-xs input-bordered"
            />
          </div>
        </div>
      );
    case "custom":
      return (
        <div className="flex flex-col w-full space-x-2">
          {header.column.columnDef.meta?.filter}
        </div>
      );
    default:
      return null;
  }
}
