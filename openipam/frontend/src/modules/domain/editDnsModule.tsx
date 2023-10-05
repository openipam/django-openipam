import React from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDnsRecord, DnsRecord } from "../../utils/types";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const EditDnsModule = (p: {
  DnsData: DnsRecord | undefined;
  domain?: string;
  host?: string;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const updateDns = async (DnsData: CreateDnsRecord) => {
    await api.dns.byId(p.DnsData!.id).update({ ...DnsData });
    p.setShowModule({
      show: false,
      DnsData: undefined,
    });
  };
  return (
    <Module
      title={"Edit DNS Record"}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          DnsData: undefined,
        });
      }}
    >
      <form
        className="flex flex-col gap-4"
        onSubmit={(e: any) => {
          e.preventDefault();
          const DnsData = {
            name: e.target["Dns-name"].value,
            ip_content: e.target["Dns-ip"].value,
            text_content: e.target["Dns-text"].value,
            dns_type: e.target["Dns-type"].value,
            ttl: e.target["Dns-ttl"].value,
            content: e.target["Dns-ip"].value || e.target["Dns-text"].value,
            id: p.DnsData!.id,
          };
          if (DnsData.ip_content === "") delete DnsData.ip_content;
          if (DnsData.text_content === "") delete DnsData.text_content;
          if (DnsData.ip_content && DnsData.text_content) {
            alert("only fill out IP Content OR Text Content");
            return;
          }
          if (
            DnsData.ip_content === undefined &&
            DnsData.text_content === undefined
          ) {
            alert("fill out IP Content OR Text Content");
            return;
          }
          if (DnsData.name === "") {
            alert("fill out Dns Name");
            return;
          }
          if (DnsData.dns_type === "") {
            alert("fill out Dns Type");
            return;
          }
          if (DnsData.ttl === "") {
            alert("fill out Dns TTL");
            return;
          }
          updateDns(DnsData);
        }}
      >
        <div className="flex flex-col gap-2">
          <label htmlFor="Dns-name">Dns Name</label>
          <input
            type="text"
            id="Dns-name"
            value={p.DnsData?.name ?? ""}
            onChange={() => {}}
            disabled
            className="input input-bordered input-primary"
          />
          {p.host && <p className="p-2">Host is {p.host}</p>}
        </div>
        <div className="flex flex-col gap-2">
          <label>Note: only fill out IP Content OR Text Content</label>
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="Dns-master">IP Content</label>
          <input
            type="text"
            id="Dns-ip"
            onChange={() => {}}
            value={
              p.DnsData?.content?.includes(".")
                ? p.DnsData?.content
                : p.DnsData?.ip_content ?? ""
            }
            className="input input-bordered input-primary"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="Dns-master">Text Content</label>
          <input
            type="text"
            id="Dns-text"
            onChange={() => {}}
            value={
              p.DnsData?.content?.includes(".")
                ? p.DnsData?.text_content
                : p.DnsData?.content ?? ""
            }
            className="input input-bordered input-primary"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="Dns-type">Type</label>
          <input
            type="text"
            id="Dns-type"
            onChange={() => {}}
            value={p.DnsData?.dns_type ?? ""}
            className="input input-bordered input-primary"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="Dns-type">TTL</label>
          <input
            type="number"
            id="Dns-ttl"
            onChange={() => {}}
            value={p.DnsData?.ttl ?? ""}
            className="input input-bordered input-primary"
          />
        </div>
        <FormFooter
          onCancel={() =>
            p.setShowModule({
              show: false,
              DnsData: undefined,
            })
          }
          onSubmit={() => {}}
          submitText="Update DNS Record"
        />
      </form>
    </Module>
  );
};
