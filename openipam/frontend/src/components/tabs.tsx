import { Edit } from "@mui/icons-material";
import React, { Dispatch, SetStateAction } from "react";

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
            className={`tab btn btn-ghost btn-outline bg-base-300 ${
              p.tab === t
                ? "btn-primary btn-disabled text-base-content"
                : "btn-ghost-secondary text-base-content"
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
  edit?: Dispatch<SetStateAction<{ show: boolean } & any>> | undefined;
}) => {
  return (
    <>
      {p.tab === p.name && p.labels && (
        <div
          className={`card w-[80%] relative md:w-[40rem] bg-base-300 shadow-xl ${p.props}`}
        >
          {p.edit && (
            <div className="absolute ml-4">
              <button
                className="btn btn-circle btn-ghost btn-xs"
                onClick={() => {
                  p.edit!({
                    show: true,
                    data: p.data,
                  });
                }}
              >
                <Edit />
              </button>
            </div>
          )}
          <div className="card-body">
            {p.data && (
              <div className="flex flex-col gap-4 mt-2">
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
      )}
      {p.tab === p.name && p.children}
    </>
  );
};
