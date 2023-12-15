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
  const [action, setAction] = useState<string>("tagNetwork");
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
              case "tagNetwork":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Add Tag(s)",
                  multiple: true,
                  onSubmit: async (e: any) => {
                    const tags = e.target[0].value.split(",");
                    await Promise.all(
                      p.rows
                        .map((network) => {
                          return [
                            ...(tags.length && tags?.[0] !== ""
                              ? [api.networks.byId(network.network).tag()]
                              : []),
                          ];
                        })
                        .flat()
                    );
                  },
                  children: (
                    <div>
                      <p>Tip: add multiple tags by separating with a comma</p>
                      <label className="label">Tags</label>
                      <input className="input input-bordered input-primary" />
                    </div>
                  ),
                });
                break;
              case "resizeNetwork":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Set Network Size",
                  onSubmit: async (v: any) => {
                    const size: string = v.target[0].value;
                    if (!size.match(/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/)) {
                      alert("invalid network size");
                      return;
                    }
                    await Promise.all(
                      p.rows.map((network) => {
                        api.networks.byId(network.network).resize();
                      })
                    );
                  },
                  children: (
                    <div className="h-80">
                      <label className="label">
                        Only increases in Network size are supported
                      </label>
                      <input className="input input-primary input-bordered" />
                    </div>
                  ),
                });
                break;
              case "releaseAbandonedLeases":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Release Abandoned Leases",
                  onSubmit: async () => {
                    await Promise.all(
                      p.rows.map((network) => {
                        api.networks.byId(network.network).realeaseAbandoned();
                      })
                    );
                  },
                  children: (
                    <div>
                      <input className="hidden" />
                    </div>
                  ),
                });
                break;
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
