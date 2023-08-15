import React, { ReactNode } from "react";

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
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-Dns-module"
        className="modal-toggle"
      />
      <dialog id="Dns-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-Dns-module"
            onClick={() =>
              p.setShowModule({
                show: false,
                DnsData: undefined,
              })
            }
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6 text-gray-500 hover:text-gray-300"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </label>
          <h1 className="text-2xl font-bold mb-4">{p.title}</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              if (p.multiple) {
                p.onSubmit?.(e);
                return;
              }
              const data = e.target[0].value;
              p.onSubmit?.(data);
            }}
          >
            {p.children}
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-outline btn-ghost"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    data: undefined,
                  })
                }
                type="reset"
              >
                Cancel
              </button>
              {p.onSubmit && (
                <button type="submit" className="btn btn-primary">
                  Submit
                </button>
              )}
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
