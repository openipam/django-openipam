import React, { useMemo } from "react";
import { useInfiniteLogs } from "../../hooks/queries/useInfiniteLogs";
import { Log } from "../../utils/types";

export const RecentLogs = () => {
  const data = useInfiniteLogs({});
  const logs = useMemo<Log[]>(() => {
    if (data.isFetching) {
      return [];
    }
    if (!data.data) {
      return [];
    }
    return data.data.pages
      .flatMap((page) => page.logs ?? page.emails)
      .splice(0, 5);
  }, [data.data]);

  return (
    <div className="w-full flex flex-col mt-2 items-center">
      <label className="label">Recent Logs:</label>
      <div className="flex flex-col gap-1">
        {logs.map((log) => (
          <div
            className="stats card card-bordered m-0.5 p-1 px-3"
            key={Math.random()}
          >
            <div className="stat-title">
              {log.change_message
                ? log.change_message
                : log.content_type + " " + log.action_flag}
              : {log.object_repr}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
