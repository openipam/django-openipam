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
      <h4>Here is some info and some options</h4>
      {/* card displayig domain information */}
      <div className="flex flex-col gap-4 m-8 justify-center items-center content-center">
        <div className="card w-[50%] md:w-[1/3] bg-gray-600 shadow-xl">
          <div className="card-body items-center">
            <div className="card-title text-2xl">Domain Info</div>
            {data.domain && (
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-1">
                  <div className="text-xl">Last Changed</div>
                  <div className="text-xl">Changed By</div>
                  <div className="text-xl">Last Check</div>
                  <div className="text-xl">Description</div>
                </div>
                <div className="col-span-2">
                  <div className="text-xl">
                    {data.domain[0].last_changed
                      ? new Date(data.domain[0].last_changed)
                          .toISOString()
                          .split("T")[0]
                      : "-"}
                  </div>
                  <div className="text-xl">
                    {data.domain[0].changed_by ?? "-"}
                  </div>
                  <div className="text-xl">
                    {data.domain[0].last_check ?? "-"}
                  </div>
                  <div className="text-xl">{data.domain[0].description}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* table for dns info */}
      <div className="flex flex-col gap-4 m-8">
        {/* <Table table={table.table} loading={false} /> */}
      </div>
    </div>
  );
};
