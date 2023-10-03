import React, { useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { NetworkAutocomplete } from "../../components/autocomplete/networkAutocomplete";
import { AddressAutocomplete } from "../../components/autocomplete/addressAutocomplete";
import { DhcpAutocomplete } from "../../components/autocomplete/dhcpGroupAutocomplete";
import { useAuth } from "../../hooks/useAuth";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";
import {
  TitledInput,
  TitledSelect,
  TitledTextArea,
  TitledToggle,
} from "../../components/forms/titledInput";
import { Show } from "../../components/logic";

export const AddHostModule = (p: {
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const auth = useAuth();
  const [host, dispatch] = useReducer(hostReducer, initHost);
  const [networkToggle, setNetworkToggle] = useState(true);
  const addressTypes = useAddressTypes().data?.addressTypes;
  const addHost = async () => {
    const results = await api.hosts.create({
      ...host,
      network: host.network?.network,
      ip_address: host.ip_address?.address,
      dhcp_group: host.dhcp_group?.name,
      ...(addressTypes?.find((t) => t.name === host.address_type)?.pool
        ? {
            pool: addressTypes?.find((t) => t.name === host.address_type)?.pool,
          }
        : {}),
    } satisfies CreateHost);
    p.setShowModule(false);
    if (results.mac === host.mac) {
      window.location.href = "/ui/#/hosts/" + host.mac;
    } else {
      alert(`${JSON.stringify(results)}`);
    }
  };
  const isDynamic = (addressType: string) => {
    return Boolean(addressTypes?.find((a) => a.name === addressType)?.pool);
  };
  return (
    <Module
      form
      title={"Add Host"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule(false);
      }}
    >
      <TitledInput
        title="Mac"
        value={host.mac ?? ""}
        onChange={(value) => {
          dispatch({ type: "mac", payload: value });
        }}
        error={host.error?.mac}
      />
      <TitledInput
        title="Host Name"
        value={host.hostname ?? ""}
        onChange={(value) => {
          dispatch({ type: "hostname", payload: value });
        }}
      />
      <TitledSelect
        title="Address Type"
        value={host.address_type ?? "Other"}
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
          title=""
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
            type={addressTypes?.find((t) => t.name === host.address_type)?.id}
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
        {Object.entries(auth?.is_ipamadmin ? adminChoices : choices).map(
          ([key, value]) => (
            <option value={key} key={key}>
              {value}
            </option>
          )
        )}
      </TitledSelect>
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
      <TitledTextArea
        title="Description"
        value={host.description ?? ""}
        onChange={(value) => {
          dispatch({ type: "description", payload: value });
        }}
      />
      <FormFooter
        onCancel={() => p.setShowModule(false)}
        onSubmit={addHost}
        submitText="Add Host"
      />
    </Module>
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

const initHost = {
  mac: "",
  hostname: "",
  network: { id: 0, network: "" },
  address_type: "Dynamic",
  ip_address: { id: 0, address: "" },
  description: "",
  expire_days: 365,
  error: {},
};

const hostReducer = (state: any, action: any) => {
  let error = {};
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
      return {
        ...state,
        address_type: action.payload,
        network: null,
        ip_address: null,
      };
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
