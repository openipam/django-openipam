import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useAddressesTable } from "./useAddressesTable";
import { Table } from "../../components/table/table";
import { useAuth } from "../../hooks/useAuth";

export const Network = () => {
  const auth = useAuth();
  const { network, range } = useParams();
  const [showModule, setShowModule] = useState(false);
  const [editModule, setEditModule] = useState(false);
  const data = useAddressesTable({
    network: network ?? "",
    range: range ?? "",
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
      <h1 className="text-4xl">
        {network}/{range}
      </h1>
      <p>
        Provide filtering and searching capabilities based on status (used,
        available, reserved), network, or domain.
      </p>
      <Table table={data.table} loading={data.loading} />
    </div>
  );
};