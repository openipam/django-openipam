import React from "react";
// import { useDomainTable } from "./useDomainsTable";
import { Table } from "../../components/table";
import { useParams } from "react-router-dom";
import { useDomainTable } from "./useDomainTable";
export const Domain = () => {
  const { domain } = useParams();
  const data = useDomainTable({ domain: domain ?? "" });

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{domain}</h1>
      <h4>Here is some info and some optionss</h4>
      {/* card displayig domain information */}
      <div className="flex flex-col gap-4 m-8 justify-center items-center content-center">
        <div className="card w-[80%] md:w-[50rem] bg-gray-600 shadow-xl">
          <div className="card-body">
            <div className="card-title text-2xl justify-center">
              Domain Info
            </div>
            {data.domain && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Last Changed:</div>
                  <div className="text-xl col-span-2">
                    {data.domain[0].last_changed
                      ? new Date(data.domain[0].last_changed)
                          .toISOString()
                          .split("T")[0]
                      : data.domain[0].changed
                      ? new Date(data.domain[0].changed)
                          .toISOString()
                          .split("T")[0]
                      : ""}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Changed By:</div>
                  <div className="text-xl col-span-2">
                    {data.domain[0].changed_by}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">User Permissions:</div>
                  <div className="text-xl col-span-2">
                    {Object.entries(data.domain[0].user_perms).map(
                      ([key, val]) => (
                        <div>
                          {key}: {val as string}
                        </div>
                      )
                    )}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Group Permissions:</div>

                  <div className="text-xl col-span-2">
                    {Object.entries(data.domain[0].group_perms).map(
                      ([key, val]) => (
                        <div>
                          {key}: {val as string}
                        </div>
                      )
                    )}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Description:</div>

                  <div className="text-xl col-span-2">
                    {data.domain[0].description}
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
    </div>
  );
};
