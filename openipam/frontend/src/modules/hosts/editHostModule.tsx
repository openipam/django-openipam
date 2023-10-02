import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { DhcpAutocomplete } from "../../components/autocomplete/dhcpGroupAutocomplete";
import { NetworkAutocomplete } from "../../components/autocomplete/networkAutocomplete";
import { AddressAutocomplete } from "../../components/autocomplete/addressAutocomplete";
import { Module } from "../../components/forms/module";
import { TitledInput, TitledSelect, TitledTextArea, TitledToggle } from "../../components/forms/titledInput";
import { Show } from "../../components/logic";
import { FormFooter } from "../../components/forms/footer";

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
    await api.hosts.byId(host.mac).update({ 
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
              <TitledSelect
                title='Address Type'
                value={host.address_type ?? 'Other'}
                onChange={(value) => {
                  dispatch({ type: "address_type", payload: value });
                }}
                >
                {addressTypes?.map(({ name, description, id }) => (
                  <option value={name} key={id}>
                    {description}
                  </option>
                ))}
              </TitledSelect>
              <Show when={!isDynamic(host.address_type)}>
                <TitledToggle
                  title="Note: Leave blank to keep the same"
                  off="IP Address"
                  on="Network"
                  value={networkToggle}
                  onChange={() => setNetworkToggle(!networkToggle)}
                  />
              </Show>
              <Show when={!isDynamic(host.address_type) && networkToggle}>
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
              </Show>
              <Show when={!isDynamic(host.address_type) && !networkToggle}>
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
            </Show>
            <TitledSelect
              title="Expires"
              value={host.expire_days ?? 0}
              onChange={(value) => {
                dispatch({ type: "expire_days", payload: value });
              }}
              >
              {Object.entries(choices).map(([key, value]) => (
                <option value={key} key={key}>
                  {value}
                </option>
              ))}
            </TitledSelect>
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
            <TitledTextArea
              title="Description"
              value={host.description ?? ''}
              onChange={(value) => {
                dispatch({ type: "description", payload: value });
              }}
              />
              <TitledToggle
                title="Disable Host"
                off="Enable"
                on="Disable"
                value={host.disabled_host ?? false}
                className="toggle-sm"
                onChange={() => {
                  dispatch({
                    type: "disabled_host",
                    payload: !host.disabled_host,
                  });
                }}
                />
            {/* If disabled is checked, add reason */}
            <Show when={host.disabled_host}>
              <TitledTextArea
                title="Reason To Disable"
                value={host.reason ?? ''}
                onChange={(value) => {
                  dispatch({ type: "reason", payload: value });
                }}
                />
            </Show>
            <FormFooter
              onCancel={() =>
                p.setShowModule({
                  show: false,
                  HostData: undefined,
                })
              }
              onSubmit={updateHost}
              submitText="Update Host"
              />
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
