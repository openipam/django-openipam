import React, { useEffect, useState } from "react";
import { Table } from "../../components/table";
import { useParams } from "react-router-dom";
import { useApi } from "../../hooks/useApi";
import { DnsRecord, Host } from "../../utils/types";
import { useAddressesTable } from "./useAddressesTable";
import { Tab, Tabs } from "../../components/tabs";
import { EditHostModule } from "./editHostModule";
import { useDnsTable } from "./useDnsTable";
import { AddDnsModule } from "../domain/addDnsModule";
import { EditDnsModule } from "../domain/editDnsModule";
import { useDhcpTable } from "./useDhcpTable";

export const HostPage = () => {
  const { mac } = useParams();
  const [HostInfo, setHostInfo] = useState<Host | undefined>();
  const [tab, setTab] = useState<typeof tabs[number]>("Info");
  const [showModule, setShowModule] = useState<boolean>(false);
  const [showEditDnsModule, setShowEditDnsModule] = useState<{
    show: boolean;
    data: DnsRecord | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const [editHost, setEditHost] = useState<{
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

  const dns = useDnsTable({
    host: HostInfo?.hostname,
    mac: HostInfo?.mac,
    setShowModule: setShowModule,
    setEditModule: setShowEditDnsModule,
  });

  const dhcpTable = useDhcpTable({
    host: HostInfo?.hostname,
    mac: HostInfo?.mac,
  });

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{mac}</h1>
      <Tabs tabs={tabs} tab={tab} setTab={setTab} props={"m-8"}>
        <Tab
          tab={tab}
          name={"Info"}
          props={"m-2 pt-4"}
          edit={setEditHost}
          data={HostInfo ?? {}}
          labels={{
            hostname: "Host Name:",
            mac: "Ethernet Address",
            changed: "Last Changed:",
            changed_by: "Changed By:",
            is_dynamic: "Type:",
            disabled_host: "Disabled Host:",
            description: "Description:",
          }}
          custom={{
            changed: HostInfo?.changed
              ? new Date(HostInfo.changed).toISOString().split("T")[0]
              : "",
            changed_by: HostInfo?.changed_by.username,
            is_dynamic: HostInfo?.is_dynamic ? "Dynamic" : "Static",
            disabled_host: HostInfo?.disabled_host ? "True" : "False",
          }}
        />
        <Tab tab={tab} name={"DNS"} props={"m-2"} data={HostInfo ?? {}}>
          <div className="flex flex-col gap-4 m-8 w-[80%]">
            <Table table={dns.table} loading={dns.loading} />
          </div>
        </Tab>
        <Tab
          tab={tab}
          name={"DHCP"}
          props={"m-2"}
          data={HostInfo ?? {}}
          labels={{
            dhcp_group: "DHCP Group:",
          }}
          custom={{
            dhcp_group: HostInfo?.dhcp_group?.name,
          }}
        >
          <div className="flex flex-col gap-4 m-8 w-[50rem]">
            <Table table={dhcpTable.table} loading={dhcpTable.loading} />
          </div>
        </Tab>
        <Tab
          tab={tab}
          name={"Addresses"}
          props={"m-2"}
          data={HostInfo?.addresses ?? {}}
        >
          <div className="flex flex-col gap-4 m-8 w-[50rem]">
            <Table table={data.table} loading={data.loading} />
          </div>
        </Tab>
        <Tab
          tab={tab}
          name={"Users"}
          props={"m-2"}
          data={HostInfo ?? {}}
          labels={{
            user_owners: "User Owners:",
          }}
          custom={{
            user_owners: HostInfo?.user_owners?.join(",\n"),
          }}
        />
        <Tab
          tab={tab}
          name={"Groups"}
          props={"m-2"}
          data={HostInfo ?? {}}
          labels={{
            group_owners: "Group Owners:",
          }}
          custom={{
            group_owners: HostInfo?.group_owners?.join(",\n"),
          }}
        />
        <Tab
          tab={tab}
          name={"Attributes"}
          props={"m-2"}
          data={HostInfo ?? {}}
          labels={{
            attributes: "Attributes:",
          }}
          custom={{
            attributes: Object.entries(HostInfo?.attributes ?? {}).map(
              (attr) => {
                return (
                  <div>
                    <div>Name: {" " + attr[0]}</div>
                    <div>Value: {" " + attr[1]}</div>
                  </div>
                );
              }
            ),
          }}
        />
      </Tabs>
      <EditHostModule
        showModule={editHost.show}
        setShowModule={setEditHost}
        HostData={editHost.data}
      />
      <AddDnsModule
        host={HostInfo?.hostname ?? ""}
        showModule={showModule}
        setShowModule={setShowModule}
      />
      <EditDnsModule
        host={HostInfo?.hostname ?? ""}
        showModule={showEditDnsModule.show}
        setShowModule={setShowEditDnsModule}
        DnsData={showEditDnsModule.data}
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
