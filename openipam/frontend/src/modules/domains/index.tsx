import React, { useState } from "react";
import { useDomainsTable } from "./useDomainsTable";
import { Table } from "../../components/table";
import { AddDomainModule } from "./addDomainModule";
import { EditDomainModule } from "./editDomainModule";

type Domain = {
  name: string;
  description: string;
  master: string;
  changed: string;
  type: string;
  notified_serial: string;
  account: string;
  last_check: string;
  //   user_perms: Record<string, string>;
  //   group_perms: Record<string, string>;
};

export const Domains = () => {
  const [showAddDomain, setShowAddDomain] = useState(false);
  const [editDomain, setEditDomain] = useState<{
    show: boolean;
    domainData: Domain | undefined;
  }>({
    show: false,
    domainData: undefined,
  });
  const table = useDomainsTable({
    setShowAddDomain: setShowAddDomain,
    setEditDomain: setEditDomain,
  });
  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Domains</h1>
      <h4>Here is some info and some options</h4>
      <div className="flex flex-col gap-4 m-8">
        <Table table={table.table} loading={false} />
      </div>
      <AddDomainModule
        showModule={showAddDomain}
        setShowModule={setShowAddDomain}
      />
      <EditDomainModule
        showModule={editDomain.show}
        setShowModule={setEditDomain}
        domainData={editDomain.domainData}
      />
    </div>
  );
};
