import React from "react";
import { useNetworksTable } from "./useNetworksTable";
import { Table } from "../../components/table";

export const Networks = () => {
  const [showModule, setShowModule] = React.useState(false);
  const [editModule, setEditModule] = React.useState(false);
  const data = useNetworksTable({
    setShowModule,
    setEditModule,
  });
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Networks</h1>
      <Table table={data.table} loading={data.loading} />
    </div>
  );
};
