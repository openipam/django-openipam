import React, { useEffect, useState } from "react";
import { Table } from "../../components/table";
import { useParams } from "react-router-dom";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";
import { useAddressesTable } from "./useAddressesTable";

export const HostPage = () => {
  const { mac } = useParams();
  const [HostInfo, setHostInfo] = useState<Host | undefined>();
  const [tab, setTab] = useState<typeof tabs[number]>("Info");
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
      <div className="tabs flex flex-row gap-4 m-8 justify-center items-center content-center">
        {tabs.map((t) => (
          <button
            key={t}
            className={`tab btn btn-ghost btn-outline ${
              tab === t
                ? "btn-primary btn-disabled disabled:text-gray-500"
                : "btn-ghost-secondary text-gray-300"
            }`}
            disabled={tab === t}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>
      {/* card displayig Host information */}
      {tab === "Info" && (
        <div className="card w-[80%] md:w-[40rem] bg-gray-600 shadow-xl">
          <div className="card-body relative">
            {HostInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Last Changed:</div>
                  <div className="text-xl col-span-2">
                    {HostInfo.changed
                      ? new Date(HostInfo.changed).toISOString().split("T")[0]
                      : ""}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Changed By:</div>
                  <div className="text-xl col-span-2">
                    {HostInfo.changed_by.username}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Type:</div>
                  <div className="text-xl col-span-2">
                    {HostInfo.is_dynamic ? "Dynamic" : "Static"}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Disabled Host:</div>

                  <div className="text-xl col-span-2">
                    {HostInfo.disabled_host ? "True" : "False"}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Description:</div>

                  <div className="text-xl col-span-2">
                    {HostInfo.description}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {tab === "DHCP" && (
        <div className="card w-[80%] md:w-[40rem] bg-gray-600 shadow-xl">
          <div className="card-body relative">
            {HostInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">DHCP Group:</div>
                  <div className="text-xl col-span-2">
                    <div>Name: {" " + HostInfo.dhcp_group?.name}</div>
                    <div>
                      Description: {" " + HostInfo.dhcp_group?.description}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {tab === "Users" && (
        <div className="card w-[80%] md:w-[40rem] bg-gray-600 shadow-xl">
          <div className="card-body relative">
            {HostInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">User Owners:</div>
                  <div className="text-xl col-span-2">
                    {HostInfo.user_owners?.join(",\n")}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {tab === "Groups" && (
        <div className="card w-[80%] md:w-[40rem] bg-gray-600 shadow-xl">
          <div className="card-body relative">
            {HostInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Group Owners:</div>

                  <div className="text-xl col-span-2">
                    {HostInfo.group_owners?.join(",\n")}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {tab === "Attributes" && (
        <div className="card w-[80%] md:w-[40rem] bg-gray-600 shadow-xl">
          <div className="card-body relative">
            {HostInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Attributes:</div>
                  <div className="text-xl col-span-2">
                    {Object.entries(HostInfo.attributes ?? {}).map((attr) => {
                      return (
                        <div>
                          <div>Name: {" " + attr[0]}</div>
                          <div>Value: {" " + attr[1]}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {tab === "Addresses" && (
        <div className="flex flex-col gap-4 m-8 w-[50rem]">
          <Table table={data.table} loading={data.loading} />
        </div>
      )}
    </div>
  );
};

const tabs = ["Info", "DHCP", "Addresses", "Users", "Groups", "Attributes"];
