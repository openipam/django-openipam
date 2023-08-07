import React from "react";
import { useLogsTable } from "./useLogsTable";
import { Table } from "../../components/table";

export const Logs = () => {
  const table = useLogsTable();
  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Logs</h1>
      <div className="flex flex-col gap-4 m-8">
        <Table table={table.table} loading={table.loading} />
      </div>
    </div>
  );
};
