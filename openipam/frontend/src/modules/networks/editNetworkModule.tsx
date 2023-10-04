import React from "react";
import { useApi } from "../../hooks/useApi";
import { Network } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

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
