import React, { useEffect, useState } from "react";
import { Table } from "../../components/table";
import { useParams } from "react-router-dom";
import { useDomainTable } from "./useDomainTable";
import { useApi } from "../../hooks/useApi";
import { AddDnsModule } from "./addDnsModule";
import { EditDnsModule } from "./editDnsModule";
import { Edit } from "@mui/icons-material";
import { EditDomainModule } from "../domains/editDomainModule";
import { DnsRecord, Domain } from "../../utils/types";

export const DomainPage = () => {
  const { domain } = useParams();
  const [domainInfo, setDomainInfo] = useState<Domain | undefined>();
  const [showModule, setShowModule] = useState<boolean>(false);
  const [showEditDomainModule, setShowEditDomainModule] = useState<{
    show: boolean;
    domainData: Domain | undefined;
  }>({
    show: false,
    domainData: undefined,
  });
  const [editModule, setEditModule] = useState<{
    show: boolean;
    DnsData: DnsRecord | undefined;
  }>({
    show: false,
    DnsData: undefined,
  });
  const data = useDomainTable({
    domain: domain ?? "",
    setShowModule,
    setEditModule,
  });
  const api = useApi();
  const getDomainInfo = async (domain: string) => {
    const results = await api.domains.byId(domain).get({});
    setDomainInfo(results);
  };
  useEffect(() => {
    if (domain) {
      getDomainInfo(domain);
    }
  }, [domain]);

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{domain}</h1>
      {/* card displayig domain information */}
      <div className="flex flex-col gap-4 m-8 justify-center items-center content-center">
        <div className="card w-[80%] md:w-[50rem] bg-gray-600 shadow-xl">
          <div className="card-body relative">
            <div className="absolute r-2">
              <button
                className="btn btn-circle btn-ghost btn-xs"
                onClick={() => {
                  setShowEditDomainModule({
                    show: true,
                    domainData: domainInfo,
                  });
                }}
              >
                <Edit />
              </button>
            </div>
            <div className="card-title text-2xl justify-center">
              Domain Info
            </div>
            {domainInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Last Changed:</div>
                  <div className="text-xl col-span-2">
                    {domainInfo.changed
                      ? new Date(domainInfo.changed).toISOString().split("T")[0]
                      : ""}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Changed By:</div>
                  <div className="text-xl col-span-2">
                    {domainInfo.changed_by}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">User Permissions:</div>
                  <div className="text-xl col-span-2">
                    {Object.entries(domainInfo.user_perms).map(([key, val]) => (
                      <div key={key}>
                        {key}: {val as string}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Group Permissions:</div>

                  <div className="text-xl col-span-2">
                    {Object.entries(domainInfo.group_perms).map(
                      ([key, val]) => (
                        <div key={key}>
                          {key}: {val as string}
                        </div>
                      )
                    )}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Description:</div>

                  <div className="text-xl col-span-2">
                    {domainInfo.description}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* table for dns info */}
      <div className="flex flex-col gap-4 m-8">
        <Table table={data.table} loading={false} />
      </div>
      <AddDnsModule
        domain={domain ?? ""}
        showModule={showModule}
        setShowModule={setShowModule}
      />
      <EditDnsModule
        domain={domain ?? ""}
        showModule={editModule.show}
        setShowModule={setEditModule}
        DnsData={editModule.DnsData}
      />
      <EditDomainModule
        domainData={domainInfo}
        showModule={showEditDomainModule.show}
        setShowModule={setShowEditDomainModule}
      />
    </div>
  );
};
