import React, { useState } from "react";
import { useHostsTable } from "./useHostsTable";
import { Table } from "../../components/table";
import { AddHostModule } from "./addHostModule";
import { EditHostModule } from "./editHostModule";
import { RenewHostModule } from "../profile/renewHostModule";
import { Host } from "../../utils/types";

export const Hosts = () => {
  const [showAddHost, setShowAddHost] = useState<boolean>(false);
  const [editHost, setEditHost] = useState<{
    show: boolean;
    HostData: any;
  }>({
    show: false,
    HostData: undefined,
  });
  const [renewModule, setRenewModule] = useState<{
    show: boolean;
    data: Host | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const table = useHostsTable({
    setShowAddHost,
    setEditHost,
    setRenewModule,
  });

  return (
    <div className="mt-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Hosts</h1>
      <div className="flex flex-col overflow-scroll gap-4 m-8">
        <Table table={table.table} loading={table.loading} />
      </div>
      <AddHostModule showModule={showAddHost} setShowModule={setShowAddHost} />
      <EditHostModule
        showModule={editHost.show}
        setShowModule={setEditHost}
        HostData={editHost.HostData}
      />
      <RenewHostModule
        HostData={renewModule.data}
        mac={renewModule.data?.mac ?? ""}
        showModule={renewModule.show}
        setShowModule={setRenewModule}
      />
    </div>
  );
};
