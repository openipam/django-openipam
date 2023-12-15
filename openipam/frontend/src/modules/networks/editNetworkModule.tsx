import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Network } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";
import { TitledInput } from "../../components/forms/titledInput";
import { SharedNetworkAutocomplete } from "../../components/autocomplete/sharedNetworkAutocomplete";
import { DhcpAutocomplete } from "../../components/autocomplete/dhcpGroupAutocomplete";

export const EditNetworkModule = (p: {
  show: boolean;
  setShow: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      network: Network | undefined;
    }>
  >;
  network: Network | undefined;
}) => {
  const api = useApi();

  const [network, dispatch] = useReducer(
    NetworkReducer,
    p.network ?? initNetwork
  );
  const [error, setError] = useState<{
    network?: string;
    name?: string;
    gateway?: string;
    description?: string;
    dhcp_group?: string;
    shared_network?: string;
    tags?: string;
    changed_by?: string;
    vlans?: string;
    buildings?: string;
    changed?: string;
  }>({});

  useEffect(() => {
    dispatch({ type: "network", payload: p.network?.network });
    dispatch({ type: "name", payload: p.network?.name });
    dispatch({ type: "gateway", payload: p.network?.gateway });
    dispatch({ type: "description", payload: p.network?.description });
    dispatch({ type: "dhcp_group", payload: p.network?.dhcp_group });
    dispatch({ type: "shared_network", payload: p.network?.shared_network });
    dispatch({ type: "tags", payload: p.network?.tags });
    dispatch({ type: "changed_by", payload: p.network?.changed_by });
    dispatch({ type: "vlans", payload: p.network?.vlans });
    dispatch({ type: "buildings", payload: p.network?.buildings });
    dispatch({ type: "changed", payload: p.network?.changed });
  }, [p.network]);

  const editNetwork = async () => {
    p.setShow({
      show: false,
      network: undefined,
    });
  };
  return (
    <Module
      title={"Edit Network"}
      showModule={p.show}
      onClose={() => {
        p.setShow({
          show: false,
          network: undefined,
        });
      }}
      form
    >
      <TitledInput
        title="Network"
        value={network.network ?? p.network?.network ?? ""}
        error={error.network}
        onChange={(value) => {
          dispatch({ type: "network", payload: value });
          if (value.match(/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/)) {
            setError({ ...error, network: "" });
          } else setError({ ...error, network: "Invalid Network" });
        }}
      />
      <TitledInput
        title="Name"
        value={network.name ?? p.network?.name ?? ""}
        error={error.name}
        onChange={(value) => {
          dispatch({ type: "name", payload: value });
          setError({ ...error, name: "" });
        }}
      />
      <TitledInput
        title="Gateway"
        value={network.gateway ?? p.network?.gateway ?? ""}
        error={error.gateway}
        onChange={(value) => {
          dispatch({ type: "gateway", payload: value });
          if (value.match(/^(\d{1,3}\.){3}\d{1,3}$/)) {
            setError({ ...error, gateway: "" });
          } else setError({ ...error, gateway: "Invalid Gateway" });
        }}
      />
      <TitledInput
        title="Description"
        value={network.description ?? p.network?.description ?? ""}
        error={error.description}
        onChange={(value) => {
          dispatch({ type: "description", payload: value });
          setError({ ...error, description: "" });
        }}
      />
      <div className="flex flex-col">
        <label className="label">DHCP Group</label>
        <DhcpAutocomplete
          DhcpId={network.dhcp_group ?? p.network?.dhcp_group}
          onDhcpChange={(value: any) => {
            dispatch({ type: "dhcp_group", payload: value });
          }}
        />
      </div>
      <div className="flex flex-col">
        <label className="label">Shared Network Name</label>
        <SharedNetworkAutocomplete
          networkName={
            network.shared_network?.name ?? p.network?.shared_network?.name
          }
          onNetworkChange={(value: any) => {
            dispatch({ type: "shared_network", payload: value });
          }}
        />
      </div>
      <TitledInput
        title="Tags"
        value={network.tags ?? p.network?.tags ?? ""}
        error={error.tags}
        onChange={(value) => {
          dispatch({ type: "tags", payload: value });
          setError({ ...error, tags: "" });
        }}
      />
      <FormFooter
        onCancel={() =>
          p.setShow({
            show: false,
            network: undefined,
          })
        }
        onSubmit={editNetwork}
        submitText="Edit Network"
      />
    </Module>
  );
};

const initNetwork: Network = {
  network: "",
  name: "",
  gateway: "",
  description: "",
  dhcp_group: "",
  shared_network: {
    id: -1,
    name: "",
    description: "",
  },
  tags: [],
  changed_by: {
    username: "",
    first_name: "",
    last_name: "",
    email: "",
  },
  vlans: [],
  buildings: [],
  changed: "",
};

const NetworkReducer = (state: Network, action: any) => {
  switch (action.type) {
    case "network":
      return { ...state, network: action.payload };
    case "name":
      return { ...state, name: action.payload };
    case "gateway":
      return { ...state, gateway: action.payload };
    case "description":
      return { ...state, description: action.payload };
    case "dhcp_group":
      return { ...state, dhcp_group: action.payload };
    case "shared_network":
      return { ...state, shared_network: action.payload };
    case "tags":
      return { ...state, tags: action.payload };
    case "changed_by":
      return { ...state, changed_by: action.payload };
    case "vlans":
      return { ...state, vlans: action.payload };
    case "buildings":
      return { ...state, buildings: action.payload };
    case "changed":
      return { ...state, changed: action.payload };
    default:
      return state;
  }
};
