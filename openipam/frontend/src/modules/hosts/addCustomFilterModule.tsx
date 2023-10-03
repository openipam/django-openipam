import React from "react";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";
import { TitledInput } from "../../components/forms/titledInput";

export const AddCustomFilterModule = (p: {
  showModule: boolean;
  setShowModule: (x: boolean) => void;
  onSubmit: (x: { name: string }) => void;
}) => {
  const [name, setName] = React.useState("");
  const onSubmit = () => {
    p.onSubmit({ name });
  };
  return (
    <Module
      title={"Set Custom Filter"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule(false);
      }}
      form
    >
      <TitledInput
        title="Name"
        value={name}
        onChange={(value) => setName(value)}
      />
      <label className="label">
        The current column filters, advanced filters, and column sorting
        currently applied to the table will be saved for immediate use.
      </label>
      <FormFooter
        onCancel={() => p.setShowModule(false)}
        onSubmit={onSubmit}
        submitText="Set Custom Filter"
      />
    </Module>
  );
};
