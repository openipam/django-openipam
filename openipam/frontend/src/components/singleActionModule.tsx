import React, { ReactNode } from "react";
import { Module } from "./forms/module";
import { FormFooter } from "./forms/footer";

export const SingleActionModule = (p: {
  data: any[];
  title: string;
  showModule: boolean;
  setShowModule: (show: any) => void;
  onSubmit?: (any: any) => void;
  children: ReactNode;
  multiple?: boolean;
}) => {
  return (
    <Module
      title={p.title}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          data: undefined,
        });
      }}
    >
      <form
        className="flex flex-col gap-4"
        onSubmit={(e: any) => {
          e.preventDefault();
          if (p.multiple) {
            p.onSubmit?.(e);
            p.setShowModule({
              show: false,
              data: undefined,
            });
            return;
          }
          const data = e.target[0].value;
          p.onSubmit?.(data);
          p.setShowModule({
            show: false,
            data: undefined,
          });
        }}
      >
        {p.children}
        <FormFooter
          onCancel={() =>
            p.setShowModule({
              show: false,
              data: undefined,
            })
          }
          onSubmit={p.onSubmit}
        />
      </form>
    </Module>
  );
};
