import React, { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { useAuth } from "../../hooks/useAuth";

export const Stats = () => {
  const api = useApi();
  const auth = useAuth();
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    if (auth?.is_ipamadmin) {
      api.admin.stats().then((res) => {
        setStats(res);
      });
    }
  }, [auth]);

  {
    /* This should reflect the 'snapshot' in reports */
  }
  return (
    <div className="flex w-full md:max-w-[90%] lg:max-w-[75%] flex-row gap-4 flex-wrap justify-center it content-center mt-4">
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title text-center">Hosts</div>
        <div className="stats">
          {Object.entries(stats)
            .splice(0, 2)
            .map(([key, value]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">{value as string | number}</div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title text-center">Leases</div>
        <div className="stats">
          {Object.entries(stats)
            .splice(2, 2)
            .map(([key, value]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">{value as string | number}</div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title text-center">Networks</div>
        <div className="stats">
          {Object.entries(stats)
            .splice(4, 2)
            .map(([key, value]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">{value as string | number}</div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title text-center">DNS Records</div>
        <div className="stats">
          {Object.entries(stats)
            .splice(6, 3)
            .map(([key, value]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">{value as string | number}</div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title text-center">Users</div>
        <div className="stats">
          {Object.entries(stats)
            .splice(9)
            .map(([key, value]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">{value as string | number}</div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
