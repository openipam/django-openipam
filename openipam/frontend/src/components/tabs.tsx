import React from "react";

export const Tabs = (p: {
  tabs: string[];
  tab: string;
  setTab: (t: string) => void;
  props?: string;
}) => {
  return (
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
  );
};
