import React, { useEffect, useState } from "react";
import { Table } from "../../components/table";
import { useParams } from "react-router-dom";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";
import { useAddressesTable } from "./useAddressesTable";
import { Tab, Tabs } from "../../components/tabs";
import { EditHostModule } from "./editHostModule";

export const HostPage = () => {
  const { mac } = useParams();
  const [HostInfo, setHostInfo] = useState<Host | undefined>();
  const [tab, setTab] = useState<typeof tabs[number]>("Info");
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
    const results = await api.hosts.byId(mac).get({});
    setHostInfo(results);
  };
  useEffect(() => {
    if (mac) {
      getHostInfo(mac);
    }
  }, [mac]);

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{mac}</h1>
      <Tabs tabs={tabs} tab={tab} setTab={setTab} props={"m-8"}>
        <Tab
          tab={tab}
          name={"Info"}
          props={"m-2"}
          edit={setEditHost}
          data={HostInfo ?? {}}
          labels={{
            hostname: "Host Name:",
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
        />
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
    </div>
  );
};

const tabs = ["Info", "DHCP", "Addresses", "Users", "Groups", "Attributes"];
