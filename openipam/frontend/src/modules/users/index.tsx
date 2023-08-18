import React from "react";
import { useUsersTable } from "./useUsersTable";
import { Table } from "../../components/table";

export const Users = () => {
  const data = useUsersTable({});
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Users</h1>
      <Table {...data} />
    </div>
  );
};
