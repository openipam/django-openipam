import React, { ReactNode, useState } from "react";
import { useParams } from "react-router-dom";
import { useAddressesTable } from "./useAddressesTable";
import { Table } from "../../components/table/table";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";
import { Address } from "../../utils/types";
import { AddAddressModule } from "./addAddressModule";
import { EditAddressModule } from "./editAddressModule";

export const Network = () => {
  const auth = useAuth();
  const { network, range } = useParams();
  const [showModule, setShowModule] = useState(false);
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);
  const [editModule, setEditModule] = React.useState({
    show: false,
    address: undefined as Address | undefined,
  });
  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: Address[] | undefined;
    title: string;
    onSubmit?: (data: Address[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
  const data = useAddressesTable({
    network: network ?? "",
    range: range ?? "",
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
      <h1 className="text-4xl">
        {network}/{range}
      </h1>
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
      <AddAddressModule show={showModule} setShow={setShowModule} />
      <EditAddressModule
        show={editModule.show}
        setShow={setEditModule}
        address={editModule.address ?? undefined}
      />
    </div>
  );
};
