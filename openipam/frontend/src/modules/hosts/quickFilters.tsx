import React, { useEffect, useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { Add } from "@mui/icons-material";
import { AddCustomFilterModule } from "./addCustomFilterModule";

type filterBtn = {
  label: string;
  filter: any[];
};

export const QuickFilters = (p: {
  setFilter: (filter: string[][]) => void;
  currentFilters: any;
  setCustomFilters: (filters: any) => void;
}) => {
  const [active, setActive] = useState<string | undefined>();
  const [showModule, setShowModule] = useState<boolean>(false);
  const auth = useAuth();
  const [buttons, setButtons] = useState<filterBtn[]>([
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
  ]);
  useEffect(() => {
    if (!auth) return;
    setButtons([
      {
        label: "Mine",
        filter: [["mine", auth.username]],
      },
      {
        label: "Group",
        filter: [["show_groups", true]],
      },
      {
        label: "Changed By Me",
        filter: [["changed_by", auth.username]],
      },
    ]);
  }, [auth]);
  const [custom, setCustom] = useState<filterBtn[]>(
    JSON.parse(localStorage.getItem("customHostQuickFilterButtons") ?? "[]")
  );
  return (
    <div className="flex flex-col gap-2 mt-2 justify-center">
      <div className="flex flex-row gap-2 justify-between">
        <label className="label">Quick Filters:</label>
        {custom.map((c) => c.label).includes(active ?? "") && (
          <button
            className="btn btn-ghost text-xs btn-sm mt-1 border-error"
            onClick={() => {
              localStorage.setItem(
                "customHostQuickFilterButtons",
                JSON.stringify(custom.filter((c) => c.label !== active))
              );
              setCustom(custom.filter((c) => c.label !== active));
              setActive(undefined);
            }}
          >
            Delete Active Custom Filter
          </button>
        )}
      </div>
      <div className="flex flex-row gap-2">
        <div className="flex flex-row btn-group btn-group-horizontal">
          {buttons.map((b: filterBtn) => (
            <button
              key={b.label}
              onClick={() => {
                p.setCustomFilters({});
                setActive((prev) => (prev === b.label ? undefined : b.label));
                p.setFilter(b.filter);
              }}
              className={`btn
            ${active === b.label ? "btn-primary focus" : "btn-outline"}`}
            >
              {b.label}
            </button>
          ))}
          {custom.map((b: filterBtn) => (
            <button
              key={b.label}
              onClick={() => {
                setActive((prev) => (prev === b.label ? undefined : b.label));
                p.setFilter([]);
                p.setCustomFilters(b.filter);
              }}
              className={`btn
            ${active === b.label ? "btn-primary focus" : "btn-outline"}`}
            >
              {b.label}
            </button>
          ))}
        </div>
        <button
          className="btn btn-ghost btn-sm btn-circle mt-2"
          onClick={() => {
            setShowModule(true);
          }}
        >
          <Add />
        </button>
      </div>
      <AddCustomFilterModule
        showModule={showModule}
        setShowModule={setShowModule}
        onSubmit={({ name }) => {
          localStorage.setItem(
            "customHostQuickFilterButtons",
            JSON.stringify([
              ...custom,
              {
                label: name,
                filter: p.currentFilters,
              },
            ])
          );
          setCustom((prev: filterBtn[]) => [
            ...prev,
            {
              label: name,
              filter: p.currentFilters,
            },
          ]);
          p.setCustomFilters(p.currentFilters);
        }}
      />
    </div>
  );
};
