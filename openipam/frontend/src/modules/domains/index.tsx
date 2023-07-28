import { DnsRecords } from "../../components/DnsRecords";
import React from "react";
export const Domains = () => {
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Domains</h1>
      <h4>Here is some info and some options</h4>
      <DnsRecords />
    </div>
  );
};
