import React, { ReactNode, useState } from "react";
import { useDomainsTable } from "./useDomainsTable";
import { Table } from "../../components/table/table";
import { AddDomainModule } from "./addDomainModule";
import { EditDomainModule } from "./editDomainModule";
import { CreateDomain, Domain } from "../../utils/types";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";

export const Domains = () => {
  const auth = useAuth();
  const [showAddDomain, setShowAddDomain] = useState(false);
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);
  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: Domain[] | undefined;
    title: string;
    onSubmit?: (data: Domain[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
  const [editDomain, setEditDomain] = useState<{
    show: boolean;
    domainData: CreateDomain | undefined;
  }>({
    show: false,
    domainData: undefined,
  });
  const table = useDomainsTable({
    setShowAddDomain,
    setEditDomain,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
    setActionModule,
  });
  return (
    <div className="m-auto mt-8 overflow-x-scroll flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Domains</h1>
      <Table
        table={table.table}
        loading={table.loading}
        showSelectColumns={selectingColumns}
        hideShowSelectColumns={() => setSelectingColumns(false)}
      />
      {auth?.is_ipamadmin && (
        <>
          <AddDomainModule
            showModule={showAddDomain}
            setShowModule={setShowAddDomain}
          />
          <EditDomainModule
            showModule={editDomain.show}
            setShowModule={setEditDomain}
            domainData={editDomain.domainData}
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
        </>
      )}
    </div>
  );
};
