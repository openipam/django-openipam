import React from "react";
import { useApi } from "../../hooks/useApi";
import { Module } from "../../components/forms/module";
import { TitledInput } from "../../components/forms/titledInput";
import { FormFooter } from "../../components/forms/footer";

export const AddDHCPDnsModule = (p: {
  domain?: string;
  host?: string;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const addDhcp = async () => {
    await api.dhcp.create(dhcp);
  };
  const [dhcp, setDhcp] = React.useState<DHCP>({
    host: p.host ?? "",
    domain: p.domain ?? "",
    ttl: 120,
  });
  return (
    <Module
      title={"Add DHCP DNS Record"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule(false);
      }}
      form
    >
      <TitledInput
        title="Hostname"
        value={dhcp.host}
        onChange={(value) => setDhcp({ ...dhcp, host: value })}
      />
      <TitledInput
        title="Domain"
        value={dhcp.domain}
        onChange={(value) => setDhcp({ ...dhcp, domain: value })}
      />
      <TitledInput
        title="TTL"
        type="number"
        value={dhcp.ttl}
        onChange={(value) => setDhcp({ ...dhcp, ttl: parseInt(value) })}
      />
      <FormFooter
        onCancel={() => p.setShowModule(false)}
        onSubmit={addDhcp}
        submitText="Add DHCP DNS Record"
      />
    </Module>
  );
};

type DHCP = {
  host: string;
  domain: string;
  ttl: number;
};
