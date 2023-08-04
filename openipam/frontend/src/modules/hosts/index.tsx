import React from "react";
import { useHostsTable } from "./useHostsTable";
import { Table } from "../../components/table";

export const Hosts = () => {
  const table = useHostsTable();

  return (
    <div className="m-auto overflow-x-scroll flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Hosts</h1>
      <div className="flex flex-col gap-4 m-8">
        <Table table={table.table} loading={table.loading} />
      </div>
    </div>
  );
};
