import React, { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";
import { Add, Delete } from "@mui/icons-material";

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
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-group-owners"
        className="modal-toggle"
      />
      <dialog id="add-group-owners" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-group-owners"
            onClick={() =>
              p.setShowModule({
                show: false,
                HostData: undefined,
              })
            }
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6 text-gray-500 hover:text-gray-300"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </label>
          <h1 className="text-2xl font-bold mb-4">Edit Group Owners</h1>
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
                    className="border border-gray-300 rounded-md p-2"
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

            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-outline btn-ghost"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    HostData: undefined,
                  })
                }
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                onClick={() => updateHost(owners)}
              >
                Update Host
              </button>
            </div>
          </div>
        </div>
      </dialog>
    </>
  );
};
