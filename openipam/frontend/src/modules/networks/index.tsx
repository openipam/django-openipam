import React, { ReactNode, useState } from "react";
import { useNetworksTable } from "./useNetworksTable";
import { Table } from "../../components/table/table";
import { useAuth } from "../../hooks/useAuth";
import { Network } from "../../utils/types";
import { SingleActionModule } from "../../components/singleActionModule";
import { AddNetworkModule } from "./addNetworkModule";
import { EditNetworkModule } from "./editNetworkModule";

export const Networks = () => {
  const auth = useAuth();

  const [showModule, setShowModule] = React.useState(false);
  const [editModule, setEditModule] = React.useState({
    show: false,
    network: undefined as Network | undefined,
  });
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);

  const [actionModule, setActionModule] =
    useState<ActionModule>(initActionModule);

  const data = useNetworksTable({
    setShowModule,
    setEditModule,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
    setActionModule,
  });

  if (!auth?.is_ipamadmin) {
    return (
      <div className="m-auto mt-8 overflow-x-scroll flex flex-col gap-2 items-center justify-center text-white">
        <h1 className="text-4xl">Permission Denied</h1>
      </div>
    );
  }

  return (
    <div className="mt-4 flex flex-col items-center justify-center">
      <h1 className="text-2xl">Networks</h1>
      <Table
        table={data.table}
        loading={data.loading}
        showSelectColumns={selectingColumns}
        hideShowSelectColumns={() => setSelectingColumns(false)}
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
      <AddNetworkModule show={showModule} setShow={setShowModule} />
      <EditNetworkModule
        show={editModule.show}
        setShow={setEditModule}
        network={editModule.network ?? undefined}
      />
    </div>
  );
};

const initActionModule = {
  show: false as boolean,
  data: undefined as Network[] | undefined,
  title: "" as string,
  onSubmit: (() => {}) as ((data: Network[]) => void) | undefined,
  children: (<></>) as ReactNode,
};

type ActionModule = Omit<typeof initActionModule, "onSubmit"> & {
  multiple?: boolean;
  onSubmit?: ((data: Network[]) => void) | undefined;
};
