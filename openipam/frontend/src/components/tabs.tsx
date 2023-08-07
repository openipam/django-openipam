import React from "react";

export const Tabs = (p: {
  tabs: string[];
  tab: string;
  setTab: (t: string) => void;
  props?: string;
  children?: React.ReactNode;
}) => {
  return (
    <>
      <div
        className={`tabs flex flex-row gap-4 justify-center items-center content-center ${p.props}`}
      >
        {p.tabs.map((t) => (
          <button
            key={t}
            className={`tab btn btn-ghost btn-outline ${
              p.tab === t
                ? "btn-primary btn-disabled disabled:text-gray-500"
                : "btn-ghost-secondary text-gray-300"
            }`}
            disabled={p.tab === t}
            onClick={() => p.setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>
      {p.children}
    </>
  );
};

export const Tab = (p: {
  tab: string;
  name: string;
  props?: string;
  data: {
    [key: string]: any;
  };
  labels?: {
    [key: string]: string;
  };
  custom?: {
    [key: string]: React.ReactNode | undefined;
  };
  children?: React.ReactNode;
}) => {
  return (
    <>
      {p.tab === p.name &&
        (p.children ? (
          p.children
        ) : (
          <div
            className={`card w-[80%] md:w-[40rem] bg-gray-600 shadow-xl ${p.props}`}
          >
            <div className="card-body relative">
              {p.data && (
                <div className="flex flex-col gap-4">
                  {Object.entries(p.labels ?? {}).map(([key, value]) => (
                    <div
                      key={key}
                      className="flex flex-row gap-2 grid-cols-3 w-full justify-between"
                    >
                      <div className="col-span-1 text-xl">{value}</div>
                      <div className="text-xl col-span-2">
                        {p.custom?.[key] ? p.custom[key] : p.data[key]}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
    </>
  );
};
