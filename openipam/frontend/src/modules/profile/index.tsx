import React, { ReactNode, useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Host, User } from "../../utils/types";
import { useUserHostsTable } from "./useUserHostsTable";
import { Table } from "../../components/table/table";
import { RenewHostModule } from "./renewHostModule";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";
import { AttributeModule } from "../hosts/attributeModule";

export const Profile = () => {
  const api = useApi();
  const auth = useAuth();
  const [renewModule, setRenewModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
  }>({
    show: false,
    data: undefined,
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
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);

  const hosts = useUserHostsTable({
    setRenewModule,

    setActionModule,
    setAttributeModule,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
  });

  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">
        Welcome, {auth?.first_name?.charAt(0).toUpperCase()}
        {auth?.first_name?.slice(1)}
      </h1>
      <p className="mt-8">Your Hosts:</p>
      <Table
        table={hosts.table}
        loading={hosts.loading}
        showSelectColumns={selectingColumns}
        hideShowSelectColumns={() => setSelectingColumns(false)}
      />
      <h2>For admins</h2>
      <p>Display total number of IP addresses, Domains, Networks, Hosts</p>
      <p>Quick add toolbar</p>
      <p>Most recent relevant Logs</p>
      <p>Other Stats/Reports</p>
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
        multiple={actionModule.multiple ?? false}
      />
      <AttributeModule
        showModule={attributeModule.show}
        setShowModule={setAttributeModule}
        data={attributeModule.data ?? []}
        delete={attributeModule.delete}
      />
    </div>
  );
};
