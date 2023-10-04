import React, { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";
import { Add, Delete } from "@mui/icons-material";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const EditUserOwnerModule = (p: {
  HostData: Host | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();

  const [owners, setOwners] = useState<string[]>([]);
  useEffect(() => {
    setOwners(p.HostData?.user_owners ?? []);
  }, [p.HostData]);
  const updateHost = async (Users: string[]) => {
    await api.hosts
      .byId(p.HostData?.mac ?? "")
      .users.put(Object.fromEntries(Users.map((user) => [user, user])));
    alert(`successfully changes user owners to ${Users}`);
    p.setShowModule({
      show: false,
      HostData: undefined,
    });
  };
  return (
    <Module
      title={"Edit User Owners"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          HostData: undefined,
        });
      }}
    >
      <div className="flex flex-col gap-4">
        {owners.map((user, i) => (
          <div className="flex flex-col gap-2" key={i}>
            <label htmlFor="host-user-owner">User Owner</label>
            <div className="flex flex-row gap-2">
              <input
                type="text"
                id="host-user-owner"
                value={user}
                onChange={(v) => {
                  const newOwners = [...owners];
                  newOwners[i] = v.target.value;
                  setOwners(newOwners);
                }}
                className="input input-primary input-bordered"
              />
              <button
                className="btn btn-error btn-sm btn-circle btn-ghost"
                onClick={() => {
                  const newOwners = [...owners];
                  newOwners.splice(i, 1);
                  setOwners(newOwners);
                }}
              >
                <Delete
                  fontSize="small"
                  color="error"
                  style={{ fill: "error", color: "error", stroke: "error" }}
                />
              </button>
            </div>
          </div>
        ))}
        <div className="flex flex-col gap-2 justify-center">
          <button
            className="btn btn-outline btn-ghost btn-sm"
            onClick={() => {
              setOwners([...(owners ?? []), ""]);
            }}
          >
            <Add fontSize="small" />
          </button>
        </div>

        <FormFooter
          onCancel={() =>
            p.setShowModule({
              show: false,
              HostData: undefined,
            })
          }
          onSubmit={() => updateHost(owners)}
          submitText="Update Host"
        />
      </div>
    </Module>
  );
};
