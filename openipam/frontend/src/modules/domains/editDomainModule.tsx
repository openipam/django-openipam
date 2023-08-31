import React from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDomain } from "../../utils/types";

export const EditDomainModule = (p: {
  domainData: CreateDomain | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const updateDomain = async (domainData: CreateDomain) => {
    const results = await api.domains
      .byId(domainData.name)
      .update({ ...domainData });
    alert(`successfully edited ${domainData.name}`);
    p.setShowModule({
      show: false,
      domainData: undefined,
    });
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
            onClick={() =>
              p.setShowModule({
                show: false,
                domainData: undefined,
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
          <h1 className="text-2xl font-bold mb-4">Edit Domain</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
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
              updateDomain(domainData);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-name">Domain Name</label>
              <input
                type="text"
                id="domain-name"
                onChange={() => {}}
                value={p.domainData?.name ?? ""}
                disabled
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-description">Description</label>
              <textarea
                id="domain-description"
                onChange={() => {}}
                value={p.domainData?.description ?? "" ?? ""}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-master">Master</label>
              <input
                type="text"
                id="domain-master"
                onChange={() => {}}
                value={p.domainData?.master ?? ""}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-type">Type</label>
              <input
                type="text"
                id="domain-type"
                onChange={() => {}}
                value={p.domainData?.type ?? ""}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-type">Notified Serial</label>
              <input
                type="text"
                id="domain-serial"
                onChange={() => {}}
                value={p.domainData?.notified_serial ?? ""}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-account">Account</label>
              <input
                type="text"
                id="domain-account"
                onChange={() => {}}
                value={p.domainData?.account ?? ""}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-last-check">Last Check</label>
              <input
                type="date"
                min={new Date(0).getTime()}
                max={new Date().getTime()}
                id="domain-check"
                onChange={() => {}}
                value={p.domainData?.last_check ?? ""}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-neutral text-neutral-content"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    domainData: undefined,
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
                Update Domain
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
