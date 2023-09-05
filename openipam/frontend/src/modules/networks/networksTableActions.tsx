import React, { ReactNode, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Network } from "../../utils/types";
import { Table } from "@tanstack/table-core";

export const NetworksTableActions = (p: {
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Network[] | undefined;
      title: string;
      onSubmit?: (data: Network[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  rows: Network[];
  table: Table<any>;
}) => {
  const [action, setAction] = useState<string>("renew");
  const api = useApi();

  return (
    <div className="flex flex-col gap-2 m-2">
      <label>Actions</label>
      <div className="flex flex-row gap-2">
        <select
          id={`actions`}
          onChange={(v) => {
            setAction(v.target.value);
          }}
          value={action}
          className="rounded-md p-2 select select-bordered w-full"
        >
          {Object.entries(actions).map(([key, value]) => (
            <option value={key} key={key}>
              {value}
            </option>
          ))}
        </select>
        <button
          className="btn btn-primary text-primary-content"
          onClick={() => {
            switch (action) {
              default:
                break;
            }
          }}
        >
          Go
        </button>
      </div>
    </div>
  );
};

const actions = {
  tagNetwork: "Tag Network",
  resizeNetwork: "Resize Network",
  releaseAbandonedLeases: "Release Abandoned Leases",
};
