import React, { ReactNode, useState } from "react";
import { useHostsTable } from "./useHostsTable";
import { Table } from "../../components/table";
import { AddHostModule } from "./addHostModule";
import { EditHostModule } from "./editHostModule";
import { RenewHostModule } from "../profile/renewHostModule";
import { Host } from "../../utils/types";
import { SingleActionModule } from "../../components/singleActionModule";

export const Hosts = () => {
  const [showAddHost, setShowAddHost] = useState<boolean>(false);
  const [editHost, setEditHost] = useState<{
    show: boolean;
    HostData: any;
  }>({
    show: false,
    HostData: undefined,
  });
  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
    title: string;
    onSubmit: (data: Host[]) => void;
    children: ReactNode;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
  const [renewModule, setRenewModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const table = useHostsTable({
    setShowAddHost,
    setEditHost,
    setRenewModule,
    setActionModule,
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
        showModule={renewModule.show}
        setShowModule={setRenewModule}
      />
      <SingleActionModule
        showModule={actionModule.show}
        setShowModule={setActionModule}
        data={actionModule.data ?? []}
        title={actionModule.title}
        onSubmit={actionModule.onSubmit}
        children={actionModule.children}
      />
    </div>
  );
};
