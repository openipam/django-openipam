import React from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDnsRecord, DnsRecord } from "../../utils/types";

//if domain, add host
//if host, add domain

export const AddDHCPDnsModule = (p: {
  domain?: string;
  host?: string;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const updateDns = async () => {};
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
            onClick={() => p.setShowModule(false)}
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
          <h1 className="text-2xl font-bold mb-4">Add DHCP DNS Record</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-name">Hostname</label>
              <input
                type="text"
                id="Dns-name"
                value={p.host ?? ""}
                onChange={() => {}}
                className="input input-bordered input-primary"
              />
              {p.host && <p className="p-2">Host is {p.host}</p>}
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-master">Domain</label>
              <input
                type="text"
                id="Dns-text"
                onChange={() => {}}
                value={p.domain ?? ""}
                className="input input-bordered input-primary"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-type">TTL</label>
              <input
                type="number"
                id="Dns-ttl"
                onChange={() => {}}
                value={120}
                className="input input-bordered input-primary"
              />
            </div>
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-neutral text-neutral-content"
                onClick={() => p.setShowModule(false)}
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary text-primary-content"
              >
                Add DHCP DNS Record
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
