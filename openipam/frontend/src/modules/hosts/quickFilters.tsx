import React, { useState } from "react";
import { useAuth } from "../../hooks/useAuth";

export const QuickFilters = (p: {
  setFilter: (filter: string[][]) => void;
  currentFilters: any;
  setCustomFilters: (filters: any) => void;
}) => {
  const [active, setActive] = useState<string | undefined>();
  const auth = useAuth();
  const [buttons, setButtons] = useState<any>([
    {
      label: "Mine",
      filter: [["mine", auth?.username]],
    },
    {
      label: "Group",
      filter: [["show_groups", true]],
    },
    {
      label: "Changed By Me",
      filter: [["changed_by", auth?.username]],
    },
    {
      label: "Custom",
      filter: JSON.parse(localStorage.getItem("customHostQuickFilter") ?? "[]"),
    },
  ]);
  return (
    <div className="flex flex-col gap-2 mt-2 justify-center">
      <div className="flex flex-row gap-2 justify-between">
        <label className="label">Quick Filters:</label>
        <button
          className="btn btn-ghost text-xs btn-sm mt-1"
          onClick={() => {
            localStorage.setItem(
              "customHostQuickFilter",
              JSON.stringify(p.currentFilters)
            );
            setButtons((prev: any) =>
              prev.map((b: any) =>
                b.label === "Custom" ? { ...b, filter: p.currentFilters } : b
              )
            );
            p.setCustomFilters(p.currentFilters);
          }}
        >
          Set Custom
        </button>
      </div>
      <div className="flex flex-row btn-group btn-group-horizontal">
        {buttons.map((b: any) => (
          <button
            key={b.label}
            onClick={() => {
              setActive((prev) => (prev === b.label ? undefined : b.label));
              if (b.label === "Custom") {
                p.setCustomFilters(b.filter);
              } else {
                p.setFilter(b.filter);
              }
            }}
            className={`btn
              ${active === b.label ? "btn-primary focus" : "btn-outline"}`}
          >
            {b.label}
          </button>
        ))}
      </div>
    </div>
  );
};
