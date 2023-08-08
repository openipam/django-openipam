import React from "react";

export const Main = () => {
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">OpenIPAM</h1>
      <p>Display total number of IP addresses, Domains, Networks, Hosts</p>
      <p>Most recent relevant Logs</p>
      <p>
        Other relevant information; ask Jay what info may be needed quickest
      </p>
    </div>
  );
};
