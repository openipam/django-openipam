import React, { ReactNode, useState } from "react";
import { useUsersTable } from "./useUsersTable";
import { Table } from "../../components/table/table";
import { User } from "../../utils/types";
import { SingleActionModule } from "../../components/singleActionModule";

export const Users = () => {
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);
  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: User[] | undefined;
    title: string;
    onSubmit?: (data: User[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
  const data = useUsersTable({
    setActionModule,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
  });
  return (
    <div className="mt-4 flex flex-col items-center justify-center">
      <h1 className="text-2xl">Users</h1>
      <Table
        {...data}
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
