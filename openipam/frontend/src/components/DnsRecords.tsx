import React, { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";

export const DnsRecords = () => {
  const api = useApi();
  const [dns, setDns] = useState<any>();
  const getDns = async () => {
    const results = await api.domains.get({});
    console.log(results);
    setDns(results.results);
  };
  useEffect(() => {
    getDns();
  }, []);

  return (
    <div className="m-4 p-8">
      <div className="flex flex-row m-4 p-4 relative">
        <pre className="m-8 p-8 absolute left-0">
          {JSON.stringify(dns, null, 2)}
        </pre>
      </div>
    </div>
  );
};
