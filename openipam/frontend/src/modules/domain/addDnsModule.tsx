import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDnsRecord, DNS_TYPES } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";
import { TitledInput, TitledSelect } from "../../components/forms/titledInput";
import { Match, Show, Switch } from "../../components/logic";

// ip for type A, ipv6
//ip needs to be an existing address

export const AddDnsModule = (p: {
  domain?: string;
  host?: string;
  ip_address?: string;
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const [dns, dispatch] = useReducer(DnsReducer, initDNs);
  const addDns = async () => {
    if (dns.ip_content === "") delete dns.ip_content;
    if (dns.text_content === "") delete dns.text_content;
    if (dns.ip_content && dns.text_content) {
      alert("only fill out IP Content OR Text Content");
      return;
    }
    delete dns.nameError;
    delete dns.ipError;
    delete dns.fqdnError;
    delete dns.category;
    if (p.domain) {
      await api.domains.byId(p.domain ?? "").dns.create({ ...dns });
      p.setShowModule(false);
    } else {
      await api.dns.create({ ...dns });
      p.setShowModule(false);
    }
  };
  useEffect(() => {
    if (p.ip_address) {
      dispatch({ type: "ip_content", payload: p.ip_address });
    }
  }, [p]);
  return (
    <Module
      title={"Add DNS Record"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule(false);
      }}
      form
    >
      <Show when={p.host}>
        <p className="p-2 mb-3">For Host {p.host}</p>
      </Show>
      <TitledSelect
        title="Type"
        value={dns.dns_type ?? ""}
        onChange={(value) => {
          dispatch({ type: "dns_type", payload: value });
          switch (value) {
            case "A":
              dispatch({ type: "ip_content", payload: p.ip_address ?? "" });
              break;
            case "PTR":
              dispatch({
                type: "name",
                payload: getReversedIp(p.ip_address ?? ""),
              });
              dispatch({ type: "text_content", payload: p.host ?? "" });
              break;
            case "CNAME":
              dispatch({ type: "text_content", payload: p.host ?? "" });
              dispatch({ type: "ip_content", payload: "" });
              break;
            case "NS":
              dispatch({ type: "ip_content", payload: "" });
              dispatch({ type: "name", payload: NSContent });
              dispatch({ type: "ttl", payload: 86400 });
              break;
            default:
              dispatch({ type: "name", payload: "" });
              dispatch({ type: "ip_content", payload: "" });
              dispatch({ type: "text_content", payload: "" });
              break;
          }
          if (reverseTypes.includes(value)) {
            dispatch({
              type: "name",
              payload: p.ip_address
                ? getReversedIp(p.ip_address)
                : p.host ?? "",
            });
          } else {
            dispatch({
              type: "name",
              payload: p.host ?? "",
            });
          }
          if (fqdnTypes.includes(value)) {
            dispatch({ type: "category", payload: "fqdn" });
          } else {
            dispatch({ type: "category", payload: "" });
          }
        }}
      >
        {DNS_TYPES.map((type) => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </TitledSelect>
      <div className="flex flex-col gap-2">
        <label htmlFor="Dns-name">Dns Name</label>
        <div className="flex flex-row gap-2">
          <input
            type="text"
            id="Dns-name"
            value={dns.name ?? p.host?.split(".").slice(0, -2).join(".") ?? ""}
            onChange={(e) => {
              dispatch({ type: "name", payload: e.target.value });
              //test if fqdn is valid
              if (fqdnRegex.test(e.target.value)) {
                console.log("valid");
                dispatch({ type: "nameError", payload: "" });
              } else {
                //test if name is IP address, if so, set type to PTR
                if (e.target.value.match(/^[0-9.]+$/)) {
                  dispatch({ type: "dns_type", payload: "PTR" });
                } else {
                  dispatch({ type: "nameError", payload: "Invalid Name" });
                }
              }
            }}
            className={`input input-primary input-bordered w-[1/2]
                  ${dns.nameError && "input-error"}`}
          />
          <input
            className="input input-primary input-bordered"
            value={`${
              reverseTypes.includes(dns.dns_type)
                ? `.${PTRNAME}`
                : p.domain
                ? `.${p.domain}`
                : dns.name
                ? ""
                : `.${p.host?.split(".").splice(-2).join(".")}`
            }`}
            onChange={() => {}}
          />
        </div>
        <Show when={dns.nameError}>
          <p className="text-xs text-error">{dns.nameError}</p>
        </Show>
      </div>
      <TitledInput
        title="TTL"
        type="number"
        value={dns.ttl ?? 14400}
        onChange={(value) => {
          dispatch({ type: "ttl", payload: parseInt(value) });
        }}
      />
      <Switch expression={dns.dns_type}>
        <Match value={reverseTypes}>
          <TitledInput
            title="Master"
            value={p.host ?? ""}
            onChange={(value) => {
              dispatch({ type: "text_content", payload: value });
            }}
          />
        </Match>
        <Match value={ipv4Types}>
          <TitledInput
            title="IP Content"
            value={dns.ip_content ?? p.ip_address ?? ""}
            onChange={(value) => {
              dispatch({ type: "ip_content", payload: value });
              //test if fqdn is valid
              if (value.match(/^[0-9.]+$/)) {
                dispatch({ type: "ipError", payload: "" });
              } else {
                dispatch({ type: "ipError", payload: "Invalid IP Address" });
              }
            }}
            error={dns.ipError}
          />
        </Match>
        <Match value={ipv6Types}>
          <TitledInput
            title="IPV6 Content"
            value={dns.text_content}
            onChange={(value) => {
              dispatch({ type: "text_content", payload: value });
            }}
          />
        </Match>
        <Match value={txtTypes}>
          <TitledInput
            title="Text Content"
            value={dns.text_content}
            onChange={(value) => {
              dispatch({ type: "text_content", payload: value });
            }}
          />
        </Match>
        <Match value={otherTypes}>
          <TitledInput
            title="Text Content"
            value={dns.text_content}
            onChange={(value) => {
              dispatch({ type: "text_content", payload: value });
            }}
          />
        </Match>
        <Match value={fqdnTypes}>
          <TitledInput
            title="FQDN Content"
            value={dns.ip_content ?? p.host ?? ""}
            onChange={(value) => {
              dispatch({ type: "ip_content", payload: value });
              //test if fqdn is valid
              if (fqdnRegex.test(p.host ?? "")) {
                dispatch({ type: "fqdnError", payload: "" });
              } else {
                dispatch({ type: "fqdnError", payload: "Invalid FQDN" });
              }
            }}
            error={dns.fqdnError}
          />
        </Match>
        <Match default>
          <TitledInput
            title="Content"
            value={dns.text_content}
            onChange={(value) => {
              dispatch({ type: "text_content", payload: value });
            }}
          />
        </Match>
      </Switch>
      <FormFooter
        onCancel={() => p.setShowModule(false)}
        onSubmit={addDns}
        submitText="Add DNS Record"
      />
    </Module>
  );
};

const initDNs = {
  name: "",
  nameError: "",
  fqdnError: "",
  category: "",
  ipError: "",
  ip_content: "",
  text_content: "",
  dns_type: "A",
  ttl: 14400,
};

type DnsState = typeof initDNs;

const DnsReducer = (state: DnsState, action: any) => {
  switch (action.type) {
    case "name":
      return { ...state, name: action.payload };
    case "ip_content":
      return { ...state, ip_content: action.payload };
    case "text_content":
      return { ...state, text_content: action.payload };
    case "dns_type":
      return { ...state, dns_type: action.payload };
    case "ttl":
      return { ...state, ttl: action.payload };
    case "nameError":
      return { ...state, nameError: action.payload };
    case "ipError":
      return { ...state, ipError: action.payload };
    case "fqdnError":
      return { ...state, fqdnError: action.payload };
    case "category":
      return { ...state, category: action.payload };
    default:
      return state;
  }
};

const txtTypes = ["TXT", "SPF", "DKIM", "DMARC"];
const ipv4Types = ["A"];
const ipv6Types = ["A6", "AAAA"];
const fqdnTypes = ["CNAME", "NS", "PTR", "MX"];
const otherTypes = ["SRV", "SOA", "SSHFP"];
const allTypes = txtTypes.concat(ipv4Types, ipv6Types, fqdnTypes, otherTypes);
const PTRNAME = "in-addr.arpa";
const reverseTypes = ["PTR", "NS", "SOA"];
const NSContent = "root1.usu.edu";
const fqdnRegex = new RegExp(
  "^(([a-z0-9-_]+.)?[a-z0-9][a-z0-9-]*.)+[a-z]{2,6}"
);

const getReversedIp = (ip: string) => {
  return ip.split(".").reverse().join(".");
};
