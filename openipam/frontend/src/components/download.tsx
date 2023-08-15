import { Download } from "@mui/icons-material";
import { Table } from "@tanstack/react-table";
import React, { useEffect, useMemo, useState } from "react";

export const ExportToCsv = (p: {
  columns: any[];
  rows: any[];
  fileName: string;
  separator?: string;
}) => {
  const [url, setUrl] = useState("");
  const rows = p.rows;
  const columns = p.columns;
  const tsv = useMemo(() => {
    return [
      columns.map((c) => c.header).join(p.separator ?? ", "),
      ...rows.map((r, i) =>
        columns.map((c) => c.accessorFn?.(r, i) || "").join(p.separator ?? ", ")
      ),
    ].join("\n");
  }, [rows, columns]);
  useEffect(() => {
    const blob = new Blob([tsv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    setUrl(url);
    return () => {
      URL.revokeObjectURL(url);
    };
  }, [tsv]);

  return (
    <a href={url} download={`${p.fileName}.csv`}>
      <Download fontSize="large" />
    </a>
  );
};
