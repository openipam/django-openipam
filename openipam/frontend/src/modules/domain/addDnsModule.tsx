import React, { useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDnsRecord, DNS_TYPES } from "../../utils/types";

// ip for type A, ipv6
//ip needs to be an existing address

const txtTypes = ["TXT", "SPF", "DKIM", "DMARC"];
const ipTypes = ["A", "A6", "AAAA"];
const fqdnTypes = ["CNAME", "NS", "PTR", "MX"];
const otherTypes = ["SRV", "SOA", "SSHFP"];
const allTypes = txtTypes.concat(ipTypes, fqdnTypes, otherTypes);

const fqdnRegex = new RegExp(
  "^(([a-z0-9-_]+.)?[a-z0-9][a-z0-9-]*.)+[a-z]{2,6}"
);

export const AddDnsModule = (p: {
  domain?: string;
  host?: string;
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const [dnsType, setDnsType] = useState<string>("A");
  const [fqdn, setFqdn] = useState<string>("");
  const [name, setName] = useState<string>("");
  const [fqdnError, setFqdnError] = useState<string>("");
  const [nameError, setNameError] = useState<string>("");
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
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    //test if fqdn is valid
                    if (fqdnRegex.test(e.target.value)) {
                      console.log("valid");
                      setNameError("");
                    } else {
                      console.log("invalid");
                      setNameError("Invalid Name");
                    }
                  }}
                  className={`input input-primary input-bordered w-[1/2]
                   ${nameError && "input-error"}`}
                />
                {p.domain && <p className="p-2">.{p.domain}</p>}
                {p.host && <p className="p-2">Host is {p.host}</p>}
              </div>
              {nameError && <p className="text-xs text-error">{nameError}</p>}
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-type">TTL</label>
              <input
                type="number"
                id="Dns-ttl"
                value={14400}
                onChange={() => {}}
                className="input input-primary input-bordered"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-type">Type</label>
              <select
                id="Dns-type"
                className="select select-bordered select-primary"
                value={dnsType}
                onChange={(e) => setDnsType(e.target.value)}
              >
                {DNS_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
            {ipTypes.includes(dnsType) && (
              <div className="flex flex-col gap-2">
                <label htmlFor="Dns-master">IP Content</label>
                <input
                  type="text"
                  id="Dns-ip"
                  className="input input-primary input-bordered"
                />
              </div>
            )}
            {txtTypes.includes(dnsType) && (
              <div className="flex flex-col gap-2">
                <label htmlFor="Dns-master">Text Content</label>
                <input
                  type="text"
                  id="Dns-text"
                  className="input input-primary input-bordered"
                />
              </div>
            )}
            {fqdnTypes.includes(dnsType) && (
              <div className="flex flex-col gap-2">
                <label htmlFor="Dns-master">FQDN Content</label>
                <input
                  type="text"
                  id="Dns-fqdn"
                  value={fqdn ?? p.host ?? ""}
                  onChange={(e) => {
                    setFqdn(e.target.value ?? "");
                    //test if fqdn is valid
                    if (fqdnRegex.test(p.host ?? "")) {
                      console.log("valid");
                      setFqdnError("");
                    } else {
                      console.log("invalid");
                      setFqdnError("Invalid FQDN");
                    }
                  }}
                  className={`input input-primary input-bordered ${
                    fqdnError && "input-error"
                  }`}
                />
                {fqdnError && <p className="text-xs text-error">{fqdnError}</p>}
              </div>
            )}
            {otherTypes.includes(dnsType) && (
              <div className="flex flex-col gap-2">
                <label htmlFor="Dns-master">Content</label>
                <input
                  type="text"
                  id="Dns-other"
                  className="input input-primary input-bordered"
                />
              </div>
            )}
            {!allTypes.includes(dnsType) && (
              <div className="flex flex-col gap-2">
                <label htmlFor="Dns-master">Content</label>
                <input
                  type="text"
                  id="Dns-other"
                  className="input input-primary input-bordered"
                />
              </div>
            )}
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
                onClick={() => p.setShowModule(false)}
              >
                Add Host
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
