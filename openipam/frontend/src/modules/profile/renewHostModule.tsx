import React from "react";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";

const choices = {
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
  10950: "30 Years",
};

export const RenewHostModule = (p: {
  HostData: Host[] | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const renewHost = async (expires: string) => {
    await Promise.all(
      p.HostData!.map(async (host) => {
        return await api.hosts.byId(host.mac).update({ expire_days: expires });
      })
    );
    alert(`successfully renewed ${p.HostData!.length} hosts`);
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
        id="add-Dns-module"
        className="modal-toggle"
      />
      <dialog id="Dns-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-Dns-module"
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
          <h1 className="text-2xl font-bold mb-4">Renew Host</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              const expires = e.target[0].value;
              renewHost(expires);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-name">Expires</label>
              <select
                id={`expires`}
                value={365}
                onChange={(v) => {}}
                className="rounded-md p-2 select select-primary select-bordered"
              >
                {Object.entries(choices).map(([key, value]) => (
                  <option value={key} key={key}>
                    {value}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-neutral text-neutral-content"
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
                className="btn btn-primary text-primary-content"
              >
                Renew
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
