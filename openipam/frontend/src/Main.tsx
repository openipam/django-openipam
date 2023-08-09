import React, { useEffect, useState } from "react";
import { useApi } from "./hooks/useApi";

export const Main = () => {
  const api = useApi();
  const [user, setUser] = useState<string | undefined>();
  useEffect(() => {
    api.user
      .get()
      .then((res) => {
        setUser(res);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">OpenIPAM</h1>
      <pre>{user && JSON.stringify(user, null, 2)}</pre>
      <p>User info</p>
      <p>Your hosts, quick renew</p>
      <h2>For admins</h2>
      <p>Display total number of IP addresses, Domains, Networks, Hosts</p>
      <p>Quick add toolbar</p>
      <p>Most recent relevant Logs</p>
      <p>Other Stats/Reports</p>
    </div>
  );
};
