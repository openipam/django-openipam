import React, { ReactNode, useEffect, useMemo, useState } from "react";
import { Table } from "../../components/table/table";
import { useParams } from "react-router-dom";
import { useApi } from "../../hooks/useApi";
import { DnsRecord, Host } from "../../utils/types";
import { useAddressesTable } from "./useAddressesTable";
import { Tab, Tabs } from "../../components/tabs";
import { EditHostModule } from "../hosts/editHostModule";
import { useDnsTable } from "./useDnsTable";
import { AddDnsModule } from "../domain/addDnsModule";
import { EditDnsModule } from "../domain/editDnsModule";
import { useDhcpTable } from "./useDhcpTable";
import { Attributes } from "../../components/atributes";
import { EditUserOwnerModule } from "./editUserOwnerModule";
import { EditGroupOwnerModule } from "./editGroupOwnerModule";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";
import { AddDHCPDnsModule } from "../domain/addDHCPModule";

export const HostPage = () => {
  const { mac } = useParams();
  const auth = useAuth();
  const [HostInfo, setHostInfo] = useState<Host | undefined>();
  const owner: boolean = useMemo(
    () =>
      Boolean(
        auth?.is_ipamadmin ||
          (auth &&
            (HostInfo?.user_owners.includes(auth?.username) ||
              HostInfo?.group_owners.some((g) => auth.groups.includes(g))))
      ),
    [auth, HostInfo]
  );
  const [tab, setTab] = useState<typeof tabs[number]>("Info");
  const [showModule, setShowModule] = useState<boolean>(false);
  const [showEditDnsModule, setShowEditDnsModule] = useState<{
    show: boolean;
    data: DnsRecord | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const [showDhcpModule, setShowDhcpModule] = useState<boolean>(false);
  const [editHost, setEditHost] = useState<{
    show: boolean;
    data: Host | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const [editUserOwner, setEditUserOwner] = useState<{
    show: boolean;
    data: Host | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const [editGroupOwner, setEditGroupOwner] = useState<{
    show: boolean;
    data: Host | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const data = useAddressesTable({
    data: HostInfo?.addresses ?? {
      static: [],
      leased: [],
    },
  });
  const api = useApi();
  const getHostInfo = async (mac: string) => {
    try {
      const results = await api.hosts.byId(mac).get({});
      setHostInfo(results);
    } catch {
      const result = await api.hosts.get({ hostname: mac });
      setHostInfo(result.results[0]);
    }
  };
  useEffect(() => {
    if (mac) {
      getHostInfo(mac);
    }
  }, [mac]);

  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: DnsRecord[] | undefined;
    title: string;
    onSubmit?: (data: DnsRecord[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });

  const dns = useDnsTable({
    host: HostInfo?.hostname,
    mac: HostInfo?.mac,
    setShowModule: setShowModule,
    setEditModule: setShowEditDnsModule,
    owner,
    setActionModule,
  });

  const dhcpTable = useDhcpTable({
    host: HostInfo?.hostname,
    mac: HostInfo?.mac,
    owner,
    setShowDhcpModule,
  });

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{mac}</h1>
      <Tabs tabs={tabs} tab={tab} setTab={setTab} props={"m-8"}>
        <Tab
          tab={tab}
          name={"Info"}
          props={"m-2 pt-4"}
          edit={owner ? setEditHost : undefined}
          data={HostInfo ?? {}}
          labels={{
            hostname: "Host Name:",
            mac: "Ethernet Address",
            expires: "Expires:",
            last_seen: "Last Seen:",
            last_seen_ip: "Last Seen IP:",
            vendor: "Vendor:",
            changed: "Last Changed:",
            changed_by: "Changed By:",
            address_type: "Type:",
            disabled_host: "Disabled Host:",
            description: "Description:",
          }}
          custom={{
            changed: HostInfo?.changed
              ? new Date(HostInfo.changed).toISOString().split("T")[0]
              : "",
            last_seen: HostInfo?.last_seen
              ? new Date(HostInfo.last_seen).toISOString().split("T")[0]
              : "> 3 months, if ever",
            last_seen_ip: HostInfo?.last_seen_ip
              ? new Date(HostInfo.last_seen_ip).toISOString().split("T")[0]
              : "> 3 months, if ever",
            changed_by: HostInfo?.changed_by.username,
            disabled_host: HostInfo?.disabled_host ? "True" : "False",
            expires:
              new Date(HostInfo?.expires ?? 0) < new Date()
                ? "Expired"
                : `${Math.ceil(
                    (new Date(HostInfo?.expires ?? 0).getTime() -
                      new Date().getTime()) /
                      (1000 * 3600 * 24)
                  )} Days Left`,
          }}
        />
        <Tab tab={tab} name={"DNS"} props={"m-2"} data={HostInfo ?? {}}>
          <Table table={dns.table} loading={dns.loading} />
        </Tab>
        <Tab
          tab={tab}
          name={"DHCP"}
          props={"m-2 pt-4"}
          edit={owner ? setEditHost : undefined}
          data={HostInfo ?? {}}
          labels={{
            dhcp_group: "DHCP Group:",
          }}
          custom={{
            dhcp_group: HostInfo?.dhcp_group?.name,
          }}
        >
          <div className="flex flex-col gap-4 m-8 w-[80rem]">
            <h2 className="text-2xl ml-8">DHCP-DNS Records</h2>
            <Table table={dhcpTable.table} loading={dhcpTable.loading} />
          </div>
        </Tab>
        <Tab
          tab={tab}
          name={"Addresses"}
          props={"m-2"}
          data={HostInfo?.addresses ?? {}}
        >
          <div className="flex flex-col gap-4 m-8 w-[80rem]">
            <Table table={data.table} loading={data.loading} />
          </div>
        </Tab>
        <Tab
          tab={tab}
          name={"Users"}
          props={"m-2 pt-4"}
          data={HostInfo ?? {}}
          labels={{
            user_owners: "User Owners:",
          }}
          custom={{
            user_owners: HostInfo?.user_owners?.join(",\n"),
          }}
          edit={owner ? setEditUserOwner : undefined}
        />
        <Tab
          tab={tab}
          name={"Groups"}
          props={"m-2 pt-4"}
          data={HostInfo ?? {}}
          labels={{
            group_owners: "Group Owners:",
          }}
          custom={{
            group_owners: HostInfo?.group_owners?.join(",\n"),
          }}
          edit={owner ? setEditGroupOwner : undefined}
        />

        <Tab tab={tab} name={"Attributes"} data={HostInfo?.attributes ?? {}}>
          <Attributes
            mac={HostInfo?.mac ?? ""}
            attributes={HostInfo?.attributes ?? {}}
            owner={owner}
          />
        </Tab>
      </Tabs>
      <EditHostModule
        showModule={editHost.show}
        setShowModule={setEditHost}
        HostData={editHost.data}
      />
      <EditUserOwnerModule
        showModule={editUserOwner.show}
        setShowModule={setEditUserOwner}
        HostData={editUserOwner.data}
      />
      <EditGroupOwnerModule
        showModule={editGroupOwner.show}
        setShowModule={setEditGroupOwner}
        HostData={editGroupOwner.data}
      />
      <AddDHCPDnsModule
        host={HostInfo?.hostname ?? ""}
        showModule={showDhcpModule}
        setShowModule={setShowDhcpModule}
      />
      <AddDnsModule
        host={HostInfo?.hostname ?? ""}
        ip_address={HostInfo?.addresses?.static[0]}
        showModule={showModule}
        setShowModule={setShowModule}
      />
      <EditDnsModule
        host={HostInfo?.hostname ?? ""}
        showModule={showEditDnsModule.show}
        setShowModule={setShowEditDnsModule}
        DnsData={showEditDnsModule.data}
      />
      <SingleActionModule
        showModule={actionModule.show}
        setShowModule={setActionModule}
        data={actionModule.data ?? []}
        title={actionModule.title}
        onSubmit={actionModule.onSubmit}
        children={actionModule.children}
        multiple={actionModule.multiple ?? false}
      />
    </div>
  );
};

const tabs = [
  "Info",
  "DNS",
  "DHCP",
  "Addresses",
  "Users",
  "Groups",
  "Attributes",
];
