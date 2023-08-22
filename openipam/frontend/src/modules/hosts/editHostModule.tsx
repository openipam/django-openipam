import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { DhcpAutocomplete } from "../../components/autocomplete/dhcpGroupAutocomplete";
import { NetworkAutocomplete } from "../../components/autocomplete/networkAutocomplete";
import { AddressAutocomplete } from "../../components/autocomplete/addressAutocomplete";

export const EditHostModule = (p: {
  HostData: Host | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const [networkToggle, setNetworkToggle] = useState(true);
  const api = useApi();
  const [host, dispatch] = useReducer(hostReducer, {
    ...p.HostData,
    expires_days: 0,
  });
  const addressTypes = useAddressTypes().data?.addressTypes;
  const updateHost = async (HostData: CreateHost) => {
    const results = await api.hosts.byId(HostData.mac).update({ ...HostData });
    alert(`successfully edited ${HostData.mac}`);
  };
  const isDynamic = (addressType: string) => {
    return Boolean(addressTypes?.find((a) => a.name === addressType)?.pool);
  };
  useEffect(() => {
    if (p.HostData)
      dispatch({ type: "reset", payload: { ...p.HostData, expires_days: 0 } });
  }, [p.HostData]);
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-Host-module"
        className="modal-toggle"
      />
      <dialog id="add-Host-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-Host-module"
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
          <h1 className="text-2xl font-bold mb-4">Update Host</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              updateHost(host);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="host-mac">Mac</label>
              <input
                type="text"
                id="host-mac"
                value={p.HostData?.mac ?? ""}
                disabled
                onChange={() => {}}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-name">Host Name</label>
              <input
                type="text"
                id="host-name"
                value={host.hostname}
                onChange={(e) =>
                  dispatch({ type: "hostname", payload: e.target.value })
                }
                className="border border-gray-300 rounded-md p-2"
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
                className="rounded-md p-2 select select-bordered"
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
                  networkId={host.network?.id}
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
                  addressId={host.address?.id}
                />
              </div>
            )}
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-name">Expires</label>
              <select
                id={`expires`}
                value={host.expire_days}
                onChange={(v) => {
                  dispatch({ type: "expire_days", payload: v.target.value });
                }}
                className="rounded-md p-2 select select-bordered"
              >
                {Object.entries(choices).map(([key, value]) => (
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
                value={host.description}
                onChange={(e) =>
                  dispatch({ type: "description", payload: e.target.value })
                }
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-last-check">Disable Host</label>
              <input
                type="checkbox"
                checked={host.disabled_host}
                onChange={() => {
                  dispatch({
                    type: "disabled_host",
                    payload: !host.disabled_host,
                  });
                }}
                id="host-disabled"
                className="border border-gray-300 rounded-md p-2 checkbox checkbox-error checkbox-sm"
              />
            </div>
            {/* If disabled is checked, add reason */}
            {host.disabled_host && (
              <div className="flex flex-col gap-2">
                <label htmlFor="host-last-check">Reason to Disable</label>
                <textarea
                  id="host-description"
                  value={p.HostData?.description ?? ""}
                  onChange={() => {}}
                  className="border border-gray-300 rounded-md p-2"
                />
              </div>
            )}
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="bg-gray-500 hover:cursor-pointer hover:bg-gray-400 rounded-md px-4 py-2"
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
                className="bg-blue-500 hover:cursor-pointer hover:bg-blue-600 rounded-md px-4 py-2 text-white"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    HostData: undefined,
                  })
                }
              >
                Update Host
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};

const choices = {
  0: "Don't Renew",
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
  10950: "30 Years",
};

const hostReducer = (state: any, action: any) => {
  switch (action.type) {
    case "mac":
      return { ...state, mac: action.payload };
    case "hostname":
      return { ...state, hostname: action.payload };
    case "address_type":
      return { ...state, address_type: action.payload };
    case "description":
      return { ...state, description: action.payload };
    case "expire_days":
      return { ...state, expire_days: action.payload };
    case "disabled_host":
      return { ...state, disabled_host: action.payload };
    case "network":
      return { ...state, network: action.payload };
    case "address":
      return { ...state, address: action.payload };
    case "dhcp_group":
      return { ...state, dhcp_group: action.payload };
    case "reset":
      return { ...action.payload };
    default:
      return state;
  }
};
