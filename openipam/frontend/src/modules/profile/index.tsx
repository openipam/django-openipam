import React, { ReactNode, useState } from "react";
import { Host } from "../../utils/types";
import { useUserHostsTable } from "./useUserHostsTable";
import { Table } from "../../components/table/table";
import { RenewHostModule } from "./renewHostModule";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";
import { AttributeModule } from "../hosts/attributeModule";
import { Stats } from "./stats";
import { QuickAddToolbar } from "./quickAddToolbar";
import { RecentLogs } from "./recentLogs";
import { Show } from "../../components/logic";

export const Profile = () => {
  const auth = useAuth();
  const [renewModule, setRenewModule] = useState<RenewModule>(initRenewModule);
  const [actionModule, setActionModule] =
    useState<ActionModule>(initActionModule);
  const [attributeModule, setAttributeModule] =
    useState<AttributeModule>(initAttributeModule);
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
    <div className="m-4 flex flex-col gap-2 content-center items-center justify-center align-middle text-center pb-12">
      <h1 className="text-4xl text-center">
        Welcome, {auth?.first_name?.charAt(0).toUpperCase()}
        {auth?.first_name?.slice(1)}
      </h1>
      <Show when={auth?.is_ipamadmin}>
        <div className="grid grid-cols-5 gap-2 mb-20 mr-5 mt-4">
          <div
            className={`grid 
              col-span-3
              `}
          >
            <Stats />
          </div>
          <div className="grid col-span-2">
            <div className="w-full flex flex-col gap-16 content-start items-start mt-2">
              <QuickAddToolbar />
              <RecentLogs />
            </div>
          </div>
        </div>
      </Show>
      <Table
        table={hosts.table}
        loading={hosts.loading}
        showSelectColumns={selectingColumns}
        hideShowSelectColumns={() => setSelectingColumns(false)}
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
    </div>
  );
};

const initActionModule = {
  show: false as boolean,
  data: undefined as Host[] | undefined,
  title: "" as string,
  onSubmit: (() => {}) as ((data: Host[]) => void) | undefined,
  children: (<></>) as ReactNode,
};

type ActionModule = Omit<typeof initActionModule, "onSubmit"> & {
  multiple?: boolean;
  onSubmit?: ((data: Host[]) => void) | undefined;
};

const initRenewModule = {
  show: false as boolean,
  data: undefined as Host[] | undefined,
  refetch: (() => {}) as VoidFunction,
};

type RenewModule = typeof initRenewModule;

const initAttributeModule = {
  show: false as boolean,
  data: undefined as Host[] | undefined,
  delete: false as boolean | undefined,
};

type AttributeModule = Omit<typeof initAttributeModule, "delete"> & {
  delete?: boolean;
};
