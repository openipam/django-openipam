import { ArrowDownward, ArrowUpward } from "@mui/icons-material";
import {
  Column,
  Header,
  HeaderGroup,
  Table,
  flexRender,
} from "@tanstack/react-table";
import { Fragment, useMemo } from "react";
import React from "react";
import { ColumnFilter } from "./columnFilter";

export const useTHBorderClasses = (
  header: Header<any, unknown>,
  headerGroup: HeaderGroup<any>,
  visibleCols: Column<any, unknown>[]
) => {
  return useMemo(() => {
    if (
      header.isPlaceholder ||
      header.index === headerGroup.headers.length - 1 ||
      header.index === 0
    )
      return "";
    const startPositionMatches = visibleCols.at(0)?.id === header.column.id;
    const endPositionMatches = visibleCols.at(-1)?.id === header.column.id;
    if (
      header.subHeaders.length > 0 ||
      (startPositionMatches && endPositionMatches)
    )
      return "border-x-base-100 border-x-8 border-y-0 border";
    if (startPositionMatches)
      return "border-x-base-100 border-l-8 border-r-0 border-y-0 border";
    if (endPositionMatches)
      return "border-x-base-100 border-l-0 border-r-8 border-y-0 border";
    return "";
  }, [header, headerGroup, visibleCols]);
};

const TableHeaderLabel = (p: {
  header: Header<any, unknown>;
  hideSorting: boolean;
  table?: Table<any>;
  footer?: boolean;
}) => {
  const header = p.header;
  const setSorting = p.table?.options.meta?.setSorting;
  const show = !p.hideSorting && !header.column.columnDef.meta?.hideSort;
  return (
    <div
      className={`whitespace-nowrap text-neutral ${
        show ? "cursor-pointer select-none" : ""
      }`}
      onClick={() => {
        if (!show) return;
        const sort = header.column.getIsSorted();
        if (sort === "asc")
          setSorting
            ? setSorting((prev: any[]) => [
                ...prev.filter((c) => c.id !== header.column.id),
                {
                  id: header.column.id,
                  desc: true,
                },
              ])
            : header.column.toggleSorting(true);
        else if (!sort)
          setSorting
            ? setSorting((prev: any[]) => [
                ...prev.filter((c) => c.id !== header.column.id),
                {
                  id: header.column.id,
                  desc: false,
                },
              ])
            : header.column.toggleSorting(false);
        else
          setSorting
            ? setSorting((prev: any[]) => [
                ...prev.filter((c) => c.id !== header.column.id),
              ])
            : header.column.clearSorting();
      }}
    >
      {flexRender(header.column.columnDef.header, {
        ...header.getContext(),
        footer: p.footer,
      })}
      {{
        asc: (
          <>
            &nbsp;
            <ArrowUpward style={{ fill: "inherit" }} />
          </>
        ),
        desc: (
          <>
            &nbsp;
            <ArrowDownward style={{ fill: "inherit" }} />
          </>
        ),
      }[!show ? "" : (header.column.getIsSorted() as string)] ?? null}
    </div>
  );
};

export const TableHeaderCell = (p: {
  header: Header<any, unknown>;
  headerGroup: HeaderGroup<any>;
  hideSorting?: boolean;
  hideFilter?: boolean;
  table: Table<any>;
  footer?: boolean;
}) => {
  const { header, headerGroup } = p;
  const visibleCols = useMemo(() => {
    return header.column.parent?.columns.filter((c) => c.getIsVisible()) ?? [];
  }, [header]);
  const headerBorderClasses = useTHBorderClasses(
    header,
    headerGroup,
    visibleCols
  );
  const thProps = header.column.columnDef.meta?.thProps?.() || {};
  const leafColumns = p.table.getAllLeafColumns().map((c) => c.id);
  return (
    <th
      {...thProps}
      className={`sticky top-0 text-center bg-neutral-content ${headerBorderClasses} ${
        thProps.className ?? ""
      }`}
      colSpan={header.colSpan}
    >
      {header.isPlaceholder ? null : (
        <>
          <TableHeaderLabel
            header={header}
            hideSorting={
              Boolean(p.hideSorting) || !leafColumns.includes(header.column.id)
            }
            table={p.table}
            footer={p.footer}
          />
          {!header.column.columnDef.meta?.hideFilter &&
            !p.hideFilter &&
            leafColumns.includes(header.column.id) && (
              <ColumnFilter
                column={header.column}
                table={p.table}
                header={header}
              />
            )}
        </>
      )}
    </th>
  );
};

export const TableHead = (p: { table: Table<any>; selectedColumns?: any }) => {
  return (
    <thead>
      <tr>
        {p.table.getAllLeafColumns().map((column) => {
          if (!column.getIsVisible()) return <Fragment key={column.id} />;
          return (
            <th
              key={column.id}
              style={{ width: column.getSize() }}
              className="h-0 p-0 m-0 bg-white"
            />
          );
        })}
      </tr>
      {p.table.getHeaderGroups().map((headerGroup) => (
        <tr key={headerGroup.id}>
          {headerGroup.headers.map((header) => (
            <TableHeaderCell
              header={header}
              headerGroup={headerGroup}
              key={header.id}
              table={p.table}
            />
          ))}
        </tr>
      ))}
    </thead>
  );
};
