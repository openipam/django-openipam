import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { NetworkAutocomplete } from "../../components/autocomplete/networkAutocomplete";
import { AddressAutocomplete } from "../../components/autocomplete/addressAutocomplete";
import { DhcpAutocomplete } from "../../components/autocomplete/dhcpGroupAutocomplete";
import { useAuth } from "../../hooks/useAuth";

export const AddHostModule = (p: {
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const auth = useAuth();
  const [host, dispatch] = useReducer(hostReducer, {
    mac: "",
    hostname: "",
    network: { id: 0, network: "" },
    address_type: "Dynamic",
    ip_address: { id: 0, address: "" },
    description: "",
    expire_days: 365,
    error: {},
  });
  const [networkToggle, setNetworkToggle] = useState(true);
  const [error, setError] = useState<{[key: string]: string}>({});
  const addressTypes = useAddressTypes().data?.addressTypes;
  const addHost = async () => {
    const results = await api.hosts.create({ 
      ...host,
       network: host.network?.network,
        ip_address: host.ip_address?.address,
      dhcp_group: host.dhcp_group?.name,
      } satisfies CreateHost);
    p.setShowModule(false);
    window.location.href = "/ui/#/hosts/" + host.mac;
  };
  const isDynamic = (addressType: string) => {
    return Boolean(addressTypes?.find((a) => a.name === addressType)?.pool);
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-host-module"
        className="modal-toggle"
      />
      <dialog id="add-host-module" className="modal">
        <div className="modal-box bg-base-100 border border-neutral-content">
          <label
            htmlFor="add-host-module"
            onClick={() => p.setShowModule(false)}
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6"
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
          <h1 className="text-2xl font-bold mb-4">Add Host</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              addHost();
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="host-mac">Mac</label>
              <input
                type="text"
                id="host-mac"
                className={`input input-primary input-bordered ${host.error?.mac ? 'input-error': ''}`}
                onChange={(e) =>
                  dispatch({ type: "mac", payload: e.target.value })
                }
              />
              {host.error?.mac && <p className="text-error">{host.error?.mac}</p>}
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-name">Host Name</label>
              <input
                type="text"
                id="host-name"
                className="input input-primary input-bordered"
                onChange={(e) =>
                  dispatch({ type: "hostname", payload: e.target.value })
                }
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="type">Address Type</label>
              <select
                id={`type`}
                value={host.address_type}
                onChange={(v) => {
                  dispatch({ type: "address_type", payload: v.target.value });
                }}
                className="select select-bordered select-primary"
              >
                {addressTypes?.map(({ name, description, id }) => (
                  <option value={name} key={id}>
                    {description}
                  </option>
                ))}
              </select>
            </div>
            {!isDynamic(host.address_type) && (
              <div className="flex flex-col gap-2 mt-2">
                <div className="flex flex-row w-full m-auto justify-center gap-1">
                  <label>IP Address</label>
                  <input
                    type="checkbox"
                    className="toggle toggle-primary mx-8"
                    checked={networkToggle}
                    onChange={() => setNetworkToggle(!networkToggle)}
                  />
                  <label>Network</label>
                </div>
              </div>
            )}
            {!isDynamic(host.address_type) && networkToggle && (
              <div className="flex flex-col gap-2">
                <label htmlFor="network">Network</label>
                <NetworkAutocomplete
                  onNetworkChange={(network) => {
                    dispatch({ type: "network", payload: network });
                  }}
                  networkId={host.network?.network}
                  addressType={
                    addressTypes?.find((t) => t.name === host.address_type)?.id
                  }
                />
              </div>
            )}
            {!isDynamic(host.address_type) && !networkToggle && (
              <div className="flex flex-col gap-2">
                <label htmlFor="network">IP Address</label>
                <AddressAutocomplete
                  onAddressChange={(address) => {
                    dispatch({ type: "address", payload: address });
                  }}
                  addressId={host.ip_address?.address}
                  type={
                    addressTypes?.find((t) => t.name === host.address_type)?.id
                  }
                  available
                />
              </div>
            )}
            <div className="flex flex-col gap-2">
              <label htmlFor="host-expires">Expires</label>
              <select
                id={`expires`}
                value={host.expire_days}
                onChange={(v) => {
                  dispatch({ type: "expire_days", payload: v.target.value });
                }}
                className="select select-bordered select-primary"
              >
                {Object.entries(auth?.is_ipamadmin ? adminChoices : choices).map(([key, value]) => (
                  <option value={key} key={key}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="dhcpGroup" className="label">
                DHCP Group (Leave blank unless otherwise directed)
              </label>
              <DhcpAutocomplete
                onDhcpChange={(dhcp) => {
                  dispatch({ type: "dhcp_group", payload: dhcp });
                }}
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-description">Description</label>
              <textarea
                id="host-description"
                className="input input-primary input-bordered"
                onChange={(e) =>
                  dispatch({ type: "description", payload: e.target.value })
                }
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

const choices = {
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
};
const adminChoices = {
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
  10950: "30 Years",
};

const hostReducer = (state: any, action: any) => {
  let error = {}
  switch (action.type) {
    case "mac":
      const regex = `^([0-9a-fA-F]{2}[:.-]?){5}[0-9a-fA-F]{2}`;
      if (!action.payload.toLowerCase().match(regex)) {
        error = { ...error, mac: "Invalid MAC Address" };
      } else {
        error = { ...error, mac: null };
      }
      return { ...state, mac: action.payload, error };
    case "hostname":
      return { ...state, hostname: action.payload };
    case "address_type":
      return { ...state, address_type: action.payload, network: null, ip_address: null };
    case "description":
      return { ...state, description: action.payload };
    case "expire_days":
      return { ...state, expire_days: action.payload };
    case "network":
      return { ...state, network: action.payload };
    case "address":
      return { ...state, ip_address: action.payload };
    case "dhcp_group":
      return { ...state, dhcp_group: action.payload };
    default:
      return state;
  }
};
