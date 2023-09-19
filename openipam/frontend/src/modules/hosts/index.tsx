import React, { ReactNode, Suspense, lazy, useState } from "react";
import { useHostsTable } from "./useHostsTable";
import { Table } from "../../components/table/table";
import { AddHostModule } from "./addHostModule";
import { EditHostModule } from "./editHostModule";
import { RenewHostModule } from "../profile/renewHostModule";
import { Host } from "../../utils/types";
import { AttributeModule } from "./attributeModule";
import { SingleActionModule } from "../../components/singleActionModule";
import { AddByCSVModule } from "./addByCsv";
import { QuickFilters } from "./quickFilters";

export const Hosts = () => {
  const [showAddHost, setShowAddHost] = useState<boolean>(false);
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);
  const [quickFilter, setQuickFilter] = useState<string[][] | undefined>();
  const [currentFilters, setCurrentFilters] = useState<any>();
  const [customFilters, setCustomFilters] = useState<any>();
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
    onSubmit?: (data: Host[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
  const [attributeModule, setAttributeModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
    delete?: boolean;
  }>({
    show: false,
    data: undefined,
    delete: false,
  });
  const [renewModule, setRenewModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
    refetch: VoidFunction;
  }>({
    show: false,
    data: undefined,
    refetch: () => {},
  });
  const [addByCsv, setAddByCsv] = useState(false);
  const table = useHostsTable({
    setShowAddHost,
    setEditHost,
    setRenewModule,
    setActionModule,
    setAttributeModule,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
    onAddByCsv: () => {
      setAddByCsv(true);
    },
    quickFilter,
    setCurrentFilters,
    customFilters,
  });

  return (
    <div className="mt-4 flex flex-col items-center justify-center">
      <h1 className="text-2xl">Hosts</h1>
      <Table
        table={table.table}
        loading={table.loading}
        showSelectColumns={selectingColumns}
        hideShowSelectColumns={() => setSelectingColumns(false)}
      />
      <QuickFilters
        setFilter={setQuickFilter}
        currentFilters={currentFilters}
        setCustomFilters={setCustomFilters}
      />
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
        refetch={renewModule.refetch}
      />
      <SingleActionModule
        showModule={actionModule.show}
        setShowModule={setActionModule}
        data={actionModule.data ?? []}
        title={actionModule.title}
        onSubmit={actionModule.onSubmit}
        children={actionModule.children}
        multiple={actionModule.multiple ?? false}
      />
      <AttributeModule
        showModule={attributeModule.show}
        setShowModule={setAttributeModule}
        data={attributeModule.data ?? []}
        delete={attributeModule.delete}
      />
      <AddByCSVModule showModule={addByCsv} setShowModule={setAddByCsv} />
    </div>
  );
};
