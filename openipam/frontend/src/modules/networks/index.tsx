import React, { ReactNode, useState } from "react";
import { useNetworksTable } from "./useNetworksTable";
import { Table } from "../../components/table/table";
import { useAuth } from "../../hooks/useAuth";
import { Network } from "../../utils/types";
import { SingleActionModule } from "../../components/singleActionModule";

export const Networks = () => {
  const auth = useAuth();
  const [showModule, setShowModule] = React.useState(false);
  const [editModule, setEditModule] = React.useState(false);
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);

  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: Network[] | undefined;
    title: string;
    onSubmit?: (data: Network[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
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
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Networks</h1>
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
    </div>
  );
};
