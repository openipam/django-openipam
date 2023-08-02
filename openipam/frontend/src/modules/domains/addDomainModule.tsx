import React from "react";
import { useApi } from "../../hooks/useApi";

type Domain = {
  name: string;
  description: string;
  master: string;
  changed: string;
  type: string;
  notified_serial: string;
  account: string;
  last_check: string;
  //   user_perms: Record<string, string>;
  //   group_perms: Record<string, string>;
};

export const AddDomainModule = (p: {
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const addDomain = async (domainData: Domain) => {
    // const results = await api.domains.create({...domainData});
    console.log(domainData);
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-domain-module"
        className="modal-toggle"
      />
      <dialog id="add-domain-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-domain-module"
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
          <h1 className="text-2xl font-bold mb-4">Add Domain</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              console.log(e);
              const domainData = {
                name: e.target[0].value,
                description: e.target[1].value,
                master: e.target[2].value,
                type: e.target[3].value,
                notified_serial: e.target[4].value,
                account: e.target[5].value,
                last_check: e.target[6].value,
                changed: new Date().toISOString(),
              };
              addDomain(domainData);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-name">Domain Name</label>
              <input
                type="text"
                id="domain-name"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-description">Description</label>
              <textarea
                id="domain-description"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-master">Master</label>
              <input
                type="text"
                id="domain-master"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-type">Type</label>
              <input
                type="text"
                id="domain-type"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-type">Notified Serial</label>
              <input
                type="text"
                id="domain-serial"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-account">Account</label>
              <input
                type="text"
                id="domain-type"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-last-check">Last Check</label>
              <input
                type="date"
                min={new Date(0).getTime()}
                max={new Date().getTime()}
                id="domain-type"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="bg-gray-500 hover:cursor-pointer hover:bg-gray-400 rounded-md px-4 py-2"
                onClick={() => p.setShowModule(false)}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-blue-500 hover:cursor-pointer hover:bg-blue-600 rounded-md px-4 py-2 text-white"
                onClick={() => p.setShowModule(false)}
              >
                Add Domain
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
