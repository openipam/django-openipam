import React, { Component } from "react";
import { render } from "react-dom";
import { DnsRecords } from "./components/DnsRecords";

export default function Main() {
  return <div>OpenIPAM
    <DnsRecords />
  </div>;
}
