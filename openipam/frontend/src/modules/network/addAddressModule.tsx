import React from "react";
import { useApi } from "../../hooks/useApi";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const AddAddressModule = (p: {
  show: boolean;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const api = useApi();
  const addAddress = async () => {
    p.setShow(false);
  };
  return (
    <Module
      title={"Add Address"}
      showModule={p.show}
      onClose={() => {
        p.setShow(false);
      }}
      form
    >
      <FormFooter
        onCancel={() => p.setShow(false)}
        onSubmit={addAddress}
        submitText="Add Address"
      />
    </Module>
  );
};
