import React from "react";

export type Domain = {
  id: number;
  name: string;
  description: string;
  changed_by: string;
  master: string;
  changed: string;
  user_perms: Record<string, string>;
  group_perms: Record<string, string>;
  type: string | undefined;
  notified_serial: string | undefined;
  account: string | undefined;
  last_check: string | undefined;
};

export type CreateDomain = Omit<
  Domain,
  "id" | "changed_by" | "changed" | "user_perms" | "group_perms"
>;

export type DnsRecord = {
  ip_content: string | undefined;
  text_content: string | undefined;
  content: string | undefined;
  name: string;
  ttl: number;
  dns_type: string;
  id: number;
  host: string;
  url: string;
};

export type CreateDnsRecord = Omit<
  DnsRecord,
  "id" | "url" | "host" | "content"
>;
