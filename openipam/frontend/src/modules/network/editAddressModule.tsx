import React from "react";
import { useApi } from "../../hooks/useApi";
import { Address } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const EditAddressModule = (p: {
  show: boolean;
  setShow: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      address: Address | undefined;
    }>
  >;
  address: Address | undefined;
}) => {
  const api = useApi();
  const editAddress = async () => {
    p.setShow({
      show: false,
      address: undefined,
    });
  };
  return (
    <Module
      title={"Edit Address"}
      showModule={p.show}
      onClose={() => {
        p.setShow({
          show: false,
          address: undefined,
        });
      }}
      form
    >
      <FormFooter
        onCancel={() =>
          p.setShow({
            show: false,
            address: undefined,
          })
        }
        onSubmit={editAddress}
        submitText="Edit Address"
      />
    </Module>
  );
};
