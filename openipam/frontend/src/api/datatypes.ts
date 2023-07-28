export interface DisabledHostData {
  reason?: string;
  changed_by?: string;
  changed_at?: string;
  disabled: boolean;
}

export interface DHCPGroupData {
  id: number;
  name: string;
  description: string;
}

export interface PoolData {
  id: number;
  name: string;
  description: string;
}

export interface UserData {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

export module HostData {
  /**
   * Data type for a host object as returned by GET endpoints
   */
  export interface GetData {
    mac: string;
    hostname: string;
    expires: string;
    description: string | null;
    is_dynamic: boolean;
    disabled_host: Required<Omit<DisabledHostData, "disabled">> | null;
    dhcp_group: number | null;
    attributes: { [key: string]: string };
    addresses: {
      leased: string[];
      static: string[];
    };
    master_ip_address: string;
    user_owners: string[];
    group_owners: string[];
    changed: string;
    changed_by: {
      first_name: string;
      last_name: string;
      username: string;
      email: string;
    };
  }

  /**
   * Data type sent to the API when creating a new host
   */
  export interface PostData {
    mac: string;
    hostname: string;
    expire_days: number;
    description: string;
    network?: string;
    pool?: string;
    ip_address?: string;
    dhcp_group?: number;
    user_owners: string[];
    group_owners: string[];
  }
}

export interface AddressData {
  address: string;
  pool: any; // TODO: Add pool data type
  reserved: boolean;
  network: string;
  changed: string;
  gateway: string;
}

export interface LeaseData {
  address: string;
  abandoned: boolean;
  server: string;
  starts: string;
  ends: string;
}

export type OwnerData = string[];

export module DNSRecordData {
  export interface GetData {
    name: string;
    content: string;
    dns_type: string;
    ttl: number;
    host: string;
    id: number;
    url: any;
  }

  export type PostData =
    | {
        name: string;
        text_content: string;
        dns_type: string;
        ttl: number;
        host: string;
      }
    | {
        name: string;
        ip_content: string;
        dns_type: string;
        ttl: number;
        host: string;
      };
}

export module DomainData {
  export interface GetData {
    id: number;
    changed_by: string;
    name: string;
    master: string | null;
    last_check: string | null;
    type: string;
    notified_serial: number | null;
    account: string | null;
    description: string | null;
    changed: string;
  }

  export type PostData = Omit<GetData, "id" | "changed_by" | "changed">;
}
