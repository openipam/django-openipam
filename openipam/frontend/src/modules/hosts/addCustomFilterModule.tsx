import React from "react";

export const AddCustomFilterModule = (p: {
  showModule: boolean;
  setShowModule: (x: boolean) => void;
  onSubmit: (x: { name: string }) => void;
}) => {
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-host-module"
        className="modal-toggle"
      />
      <dialog id="add-host-module" className="modal">
        <div className="modal-box bg-base-100 border border-neutral-content">
          <label
            htmlFor="add-host-module"
            onClick={() => p.setShowModule(false)}
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6"
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
          <h1 className="text-2xl font-bold mb-4">Set Custom Filter</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              p.onSubmit({ name: e.target["name"].value });
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="name">Name</label>
              <input
                type="text"
                id="name"
                className={`input input-primary input-bordered`}
              />
            </div>
            <label className="label">
              The current column filters, advanced filters, and column sorting
              currently applied to the table will be saved for immediate use.
            </label>
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-neutral text-neutral-content"
                onClick={() => p.setShowModule(false)}
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary text-primary-content"
                onClick={() => p.setShowModule(false)}
              >
                Set Custom Filter
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
