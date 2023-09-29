import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { DhcpAutocomplete } from "../../components/autocomplete/dhcpGroupAutocomplete";
import { NetworkAutocomplete } from "../../components/autocomplete/networkAutocomplete";
import { AddressAutocomplete } from "../../components/autocomplete/addressAutocomplete";
import { Module } from "../../components/module";
import { TitledInput } from "../../components/titledInput";

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
  const updateHost = async () => {
    if (host.expire_days === 0) delete host.expire_days;
    const results = await api.hosts.byId(host.mac).update({ 
      ...host,
       network: host.network?.network,
        ip_address: host.ip_address?.address,
      dhcp_group: host.dhcp_group?.name,
      } satisfies CreateHost);
  };
  const isDynamic = (addressType: string) => {
    return Boolean(addressTypes?.find((a) => a.name === addressType)?.pool);
  };
  useEffect(() => {
    if (p.HostData)
      dispatch({
        type: "reset",
        payload: {
          ...p.HostData,
          expire_days: 0,
          dhcp_group: p.HostData?.dhcp_group?.id,
        },
      });
  }, [p.HostData]);
  return (
    <Module title={'Update Host'} showModule={p.showModule} onClose={() => {
      p.setShowModule({
        show: false,
        HostData: undefined,
      })
    }}>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              updateHost();
            }}
            >
              <TitledInput
                title='Mac'
                value={p.HostData?.mac ?? host.mac ?? ''}
                onChange={() => {}}
                disabled
              />
              <TitledInput
                title='Host Name'
                value={host.hostname ?? ''}
                onChange={(value) => {
                  dispatch({ type: "hostname", payload: value });
                }}
              />
              
            <div className="flex flex-col gap-2">
              <label htmlFor="type">Address Type</label>
              <select
                id={`type`}
                value={host.address_type ?? 'Other'}
                onChange={(v) => {
                  dispatch({ type: "address_type", payload: v.target.value });
                }}
                className="rounded-md p-2 select select-primary select-bordered"
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
                <label>Note: Leave blank to keep the same</label>
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
              <label htmlFor="Dns-name">Expires</label>
              <select
                id={`expires`}
                value={host.expire_days ?? 0}
                onChange={(v) => {
                  dispatch({ type: "expire_days", payload: v.target.value });
                }}
                className="rounded-md p-2 select select-bordered select-primary"
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
                DhcpId={host.dhcp_group}
                />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-description">Description</label>
              <textarea
                id="host-description"
                value={host.description ?? ''}
                onChange={(e) =>
                  dispatch({ type: "description", payload: e.target.value })
                }
                className="input input-primary input-bordered"
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
                className="toggle toggle-primary toggle-sm"
                />
            </div>
            {/* If disabled is checked, add reason */}
            {host.disabled_host && (
              <div className="flex flex-col gap-2">
                <label htmlFor="host-last-check">Reason to Disable</label>
                <textarea
                  id="host-reason"
                  value={""}
                  onChange={(e) => {
                    dispatch({ type: "reason", payload: e.target.value });
                  }}
                  className="input input-primary input-bordered"
                  />
              </div>
            )}
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
          </Module>
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
      return { ...state, address_type: action.payload, network: null, ip_address: null };
    case "description":
      return { ...state, description: action.payload };
    case "expire_days":
      return { ...state, expire_days: action.payload };
    case "disabled_host":
      return { ...state, disabled_host: action.payload };
    case "network":
      return { ...state, network: action.payload };
    case "address":
      return { ...state, ip_address: action.payload };
    case "dhcp_group":
      return { ...state, dhcp_group: action.payload };
    case "reason":
      return { ...state, reason: action.payload };
    case "reset":
      return { ...action.payload };
    default:
      return state;
  }
};
