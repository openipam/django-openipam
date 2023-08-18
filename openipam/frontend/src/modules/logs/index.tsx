import React from "react";
import { useLogsTable } from "./useLogsTable";
import { Table } from "../../components/table";
import { useAuth } from "../../hooks/useAuth";

export const Logs = () => {
  const auth = useAuth();
  const table = useLogsTable();
  if (!auth?.is_ipamadmin) {
    return (
      <div className="m-auto mt-8 overflow-x-scroll flex flex-col gap-2 items-center justify-center text-white">
        <h1 className="text-4xl">Permission Denied</h1>
      </div>
    );
  }
  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Logs</h1>
      <Table table={table.table} loading={table.loading} />
    </div>
  );
};
