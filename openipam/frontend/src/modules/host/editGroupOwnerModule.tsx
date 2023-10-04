import React, { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";
import { Add, Delete } from "@mui/icons-material";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const EditGroupOwnerModule = (p: {
  HostData: Host | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const [owners, setOwners] = useState<string[]>([]);
  useEffect(() => {
    setOwners(p.HostData?.group_owners ?? []);
  }, [p.HostData]);
  const updateHost = async (Groups: string[]) => {
    await api.hosts
      .byId(p.HostData?.mac ?? "")
      .groups.put(Object.fromEntries(Groups.map((group) => [group, group])));
    alert(`successfully changes group owners to ${Groups}`);
    p.setShowModule({
      show: false,
      HostData: undefined,
    });
  };
  return (
    <Module
      title={"Edit Group Owners"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          HostData: undefined,
        });
      }}
    >
      <div className="flex flex-col gap-4">
        {owners.map((group, i) => (
          <div className="flex flex-col gap-2">
            <label htmlFor="host-group-owner">Group</label>
            <div className="flex flex-row gap-2">
              <input
                type="text"
                id="host-group-owner"
                value={group}
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
                <Delete fontSize="small" color="error" />
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
