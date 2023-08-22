import React from "react";
import { useNetworksTable } from "./useNetworksTable";
import { Table } from "../../components/table/table";
import { useAuth } from "../../hooks/useAuth";

export const Networks = () => {
  const auth = useAuth();
  const [showModule, setShowModule] = React.useState(false);
  const [editModule, setEditModule] = React.useState(false);
  const data = useNetworksTable({
    setShowModule,
    setEditModule,
  });
  if (!auth?.is_ipamadmin) {
    return (
      <div className="m-auto mt-8 overflow-x-scroll flex flex-col gap-2 items-center justify-center text-white">
        <h1 className="text-4xl">Permission Denied</h1>
      </div>
    );
  }
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Networks</h1>
      <Table table={data.table} loading={data.loading} />
    </div>
  );
};
