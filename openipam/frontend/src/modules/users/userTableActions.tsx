import React, { ReactNode, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { User } from "../../utils/types";
import { Table } from "@tanstack/table-core";
import { GroupAutocomplete } from "../../components/autocomplete/groupAutocomplete";

export const UserTableActions = (p: {
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: User[] | undefined;
      title: string;
      onSubmit?: (data: any) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  rows: User[];
  table: Table<any>;
  refetch: () => void;
}) => {
  const [action, setAction] = useState<string>("assignGroups");
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
            console.log(action);
            switch (action) {
              case "assignGroups":
                console.log(p.rows);
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Assign Groups",
                  onSubmit: async (v: any) => {
                    await Promise.all(
                      p.rows.map((user) => {
                        api.user.groups.join({
                          groups: v?.split(",") ?? [],
                          username: user.username,
                        });
                      })
                    );
                    p.refetch();
                  },
                  children: (
                    <div className="h-96">
                      <GroupAutocomplete onGroupChange={(v) => {}} />
                    </div>
                  ),
                });
                break;
              case "removeGroups":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Remove Groups",
                  onSubmit: async (v: any) => {
                    await Promise.all(
                      p.rows.map((user) => {
                        api.user.groups.leave({
                          groups: v?.split(",") ?? [],
                          username: user.username,
                        });
                      })
                    );
                    p.refetch();
                  },
                  children: (
                    <div className="h-96">
                      <GroupAutocomplete onGroupChange={(v) => {}} />
                    </div>
                  ),
                });
                break;
              case "assignObjectPermissions":
              case "populateUser":
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
  assignGroups: "Assign Groups",
  removeGroups: "Remove Groups",
  assignObjectPermissions: "Assign Object Permissions",
  populateUser: "Populate User From LDAP",
};
