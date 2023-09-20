import React, { ReactNode, useState } from "react";
import { useUsersTable } from "./useUsersTable";
import { Table } from "../../components/table/table";
import { User } from "../../utils/types";
import { SingleActionModule } from "../../components/singleActionModule";

export const Users = () => {
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
  });
  return (
    <div className="m-4 pb-20 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Users</h1>
      <Table {...data} />

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
