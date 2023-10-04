import React from "react";
import { useApi } from "../../hooks/useApi";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const AddNetworkModule = (p: {
  show: boolean;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const api = useApi();
  const addNetwork = async () => {
    p.setShow(false);
  };
  return (
    <Module
      title={"Add Network"}
      showModule={p.show}
      onClose={() => {
        p.setShow(false);
      }}
      form
    >
      <FormFooter
        onCancel={() => p.setShow(false)}
        onSubmit={addNetwork}
        submitText="Add Network"
      />
    </Module>
  );
};
