import React from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDnsRecord } from "../../utils/types";

// ip for type A, ipv6
//ip needs to be an existing address

export const AddDnsModule = (p: {
  domain?: string;
  host?: string;
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const addDns = async (DnsData: CreateDnsRecord) => {
    if (p.domain) {
      const results = await api.domains
        .byId(p.domain ?? "")
        .dns.create({ ...DnsData });
      alert(`successfully created ${DnsData.name}`);
      p.setShowModule(false);
    } else {
      const results = await api.dns.create({ ...DnsData });
      alert(`successfully created ${DnsData.name}`);
      p.setShowModule(false);
    }
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
      <dialog id="add-Dns-module" className="modal">
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
          <h1 className="text-2xl font-bold mb-4">Add Dns Record</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              const DnsData = {
                name: e.target["Dns-name"].value,
                ip_content: e.target["Dns-ip"].value,
                text_content: e.target["Dns-text"].value,
                dns_type: e.target["Dns-type"].value,
                ttl: e.target["Dns-ttl"].value,
              };
              //   if (DnsData.ip_content === "") delete DnsData.ip_content;
              //   if (DnsData.text_content === "") delete DnsData.text_content;
              //   if (DnsData.ip_content && DnsData.text_content) {
              //     alert("only fill out IP Content OR Text Content");
              //     return;
              //   }
              //   if (
              //     DnsData.ip_content === undefined &&
              //     DnsData.text_content === undefined
              //   ) {
              //     alert("fill out IP Content OR Text Content");
              //     return;
              //   }
              //   if (DnsData.name === "") {
              //     alert("fill out Dns Name");
              //     return;
              //   }
              //   if (DnsData.dns_type === "") {
              //     alert("fill out Dns Type");
              //     return;
              //   }
              //   if (DnsData.ttl === "") {
              //     alert("fill out Dns TTL");
              //     return;
              //   }
              addDns(DnsData);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-name">Dns Name</label>
              <div className="flex flex-row gap-2">
                <input
                  type="text"
                  id="Dns-name"
                  className="border border-gray-300 rounded-md p-2 w-[1/2]"
                />
                {p.domain && <p className="p-2">.{p.domain}</p>}
                {p.host && <p className="p-2">Host is {p.host}</p>}
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <label>Note: only fill out IP Content OR Text Content</label>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-master">IP Content</label>
              <input
                type="text"
                id="Dns-ip"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-master">Text Content</label>
              <input
                type="text"
                id="Dns-text"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-type">Type</label>
              <input
                type="text"
                id="Dns-type"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-type">TTL</label>
              <input
                type="number"
                id="Dns-ttl"
                value={14400}
                onChange={() => {}}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="bg-gray-500 hover:cursor-pointer hover:bg-gray-400 rounded-md px-4 py-2"
                onClick={() => p.setShowModule(false)}
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-blue-500 hover:cursor-pointer hover:bg-blue-600 rounded-md px-4 py-2 text-white"
                onClick={() => p.setShowModule(false)}
              >
                Add Dns
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
