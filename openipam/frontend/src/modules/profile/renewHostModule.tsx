import React from "react";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";
import { TitledSelect } from "../../components/forms/titledInput";

const choices = {
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
  10950: "30 Years",
};

export const RenewHostModule = (p: {
  HostData: Host[] | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
  refetch: () => void;
}) => {
  const api = useApi();
  const [expires, setExpires] = React.useState(365);
  const renewHost = async () => {
    await Promise.all(
      p.HostData!.map(async (host) => {
        return await api.hosts.byId(host.mac).update({ expire_days: expires });
      })
    );
    p.setShowModule({
      show: false,
      HostData: undefined,
    });
    p.refetch();
  };
  return (
    <Module
      title={"Renew Host"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          HostData: undefined,
        });
      }}
    >
      <TitledSelect
        title="Expires"
        value={expires}
        onChange={(value) => {
          setExpires(value as number);
        }}
      >
        {Object.entries(choices).map(([key, value]) => (
          <option value={key} key={key}>
            {value}
          </option>
        ))}
      </TitledSelect>
      <FormFooter
        onCancel={() =>
          p.setShowModule({
            show: false,
            HostData: undefined,
          })
        }
        onSubmit={renewHost}
        submitText="Renew"
      />
    </Module>
  );
};
