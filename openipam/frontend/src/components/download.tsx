import { Download } from "@mui/icons-material";
import React, { useEffect, useMemo, useState } from "react";
import { IdToName } from "./idToName";
import { Column } from "@tanstack/table-core";

export const ExportToCsv = (p: {
  columns: Column<any>[];
  rows: any[];
  fileName: string;
  separator?: string;
  askVisible?: boolean;
}) => {
  const [url, setUrl] = useState("");
  const [onlyVisible, setOnlyVisible] = useState(true);
  const rows = p.rows;
  const columns = p.columns;
  const tsv = useMemo(() => {
    return [
      columns
        .filter((c) => {
          return !onlyVisible || c.getIsVisible();
        })
        .map((c) => IdToName(c.columnDef.id ?? ""))
        .join(p.separator ?? ", "),
      ...rows.map((r, i) =>
        columns
          .filter((c) => {
            return !onlyVisible || c.getIsVisible();
          })
          .map(
            (c) =>
              (c.accessorFn?.(r, i) as string)
                .replace(",", "")
                .replace("\t", " ") || ""
          )
          .join(p.separator ?? ", ")
      ),
    ].join("\n");
  }, [rows, columns, onlyVisible, p.separator]);
  useEffect(() => {
    const blob = new Blob([tsv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    setUrl(url);
    return () => {
      URL.revokeObjectURL(url);
    };
  }, [tsv]);

  return (
    <div className="flex flex-col gap-4 items-center align-middle justify-center content-center">
      {p.askVisible && (
        <>
          <label className="text-lg">Only include visible columns?</label>
          <input
            type="checkbox"
            checked={onlyVisible}
            onChange={(e) => setOnlyVisible(e.target.checked)}
            className="toggle toggle-md toggle-primary input mb-4"
          />
        </>
      )}
      <a href={url} download={`${p.fileName}.csv`} className="text-neutral">
        <Download fontSize="large" style={{ fill: "inherit" }} />
      </a>
    </div>
  );
};
