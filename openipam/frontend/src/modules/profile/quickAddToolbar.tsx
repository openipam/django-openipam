import React, { useState } from "react";
import { AddHostModule } from "../hosts/addHostModule";
import { AddDnsModule } from "../domain/addDnsModule";

export const QuickAddToolbar = () => {
  const [showHost, setShowHost] = useState(false);
  const [showDns, setShowDns] = useState(false);

  return (
    <div className="w-full flex flex-col gap-2 mt-2 items-center">
      <label className="label">Quick Add:</label>

      <div className="flex flex-row btn-group btn-group-horizontal">
        <button
          onClick={() => {
            setShowHost(true);
          }}
          className={`btn
            btn-outline`}
        >
          Host
        </button>
        <button
          onClick={() => {
            setShowDns(true);
          }}
          className={`btn
            btn-outline`}
        >
          DNS Record
        </button>
      </div>
      <AddHostModule showModule={showHost} setShowModule={setShowHost} />
      <AddDnsModule showModule={showDns} setShowModule={setShowDns} />
    </div>
  );
};
