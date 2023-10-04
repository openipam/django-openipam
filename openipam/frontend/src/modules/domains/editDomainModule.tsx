import React, { useEffect, useReducer } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDomain } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";
import { TitledInput } from "../../components/forms/titledInput";

export const EditDomainModule = (p: {
  domainData: CreateDomain | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const [domain, dispatch] = useReducer(domainReducer, initDomain);
  const updateDomain = async () => {
    await api.domains.byId(domain.name).update({ ...domain });
    p.setShowModule({
      show: false,
      domainData: undefined,
    });
  };
  useEffect(() => {
    if (p.domainData) {
      dispatch({ type: "all", payload: p.domainData });
    }
  }, [p]);
  return (
    <Module
      title={"Edit Domain"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          domainData: undefined,
        });
      }}
      form
    >
      <TitledInput
        title="Name"
        value={domain.name}
        onChange={(value) => dispatch({ type: "name", payload: value })}
      />
      <TitledInput
        title="Description"
        value={domain.description}
        onChange={(value) => dispatch({ type: "description", payload: value })}
      />
      <TitledInput
        title="Master"
        value={domain.master}
        onChange={(value) => dispatch({ type: "master", payload: value })}
      />
      <TitledInput
        title="Type"
        value={domain.type}
        onChange={(value) => dispatch({ type: "type", payload: value })}
      />
      <TitledInput
        title="Notified Serial"
        value={domain.notified_serial}
        onChange={(value) =>
          dispatch({ type: "notified_serial", payload: value })
        }
      />
      <TitledInput
        title="Account"
        value={domain.account}
        onChange={(value) => dispatch({ type: "account", payload: value })}
      />
      <TitledInput
        title="Last Check"
        value={domain.last_check}
        type="date"
        props={{
          min: new Date(0).getTime(),
          max: new Date().getTime(),
        }}
        onChange={(value) => dispatch({ type: "last_check", payload: value })}
      />
      <FormFooter
        onCancel={() => p.setShowModule(false)}
        onSubmit={updateDomain}
        submitText="Edit Domain"
      />
    </Module>
  );
};

const initDomain = {
  name: "",
  description: "",
  master: "",
  type: "",
  notified_serial: "",
  account: "",
  last_check: "",
  changed: new Date().toISOString(),
};

const domainReducer = (state: any, action: any) => {
  switch (action.type) {
    case "name":
      return { ...state, name: action.payload };
    case "description":
      return { ...state, description: action.payload };
    case "master":
      return { ...state, master: action.payload };
    case "type":
      return { ...state, type: action.payload };
    case "notified_serial":
      return { ...state, notified_serial: action.payload };
    case "account":
      return { ...state, account: action.payload };
    case "last_check":
      return { ...state, last_check: action.payload };
    case "all":
      return { ...state, ...action.payload };
    default:
      return state;
  }
};
