import React from "react";

export const Module = (p: {
  children: React.ReactNode;
  title: string;
  showModule: boolean;
  onClose: () => void;
}) => {
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id={p.title}
        className="modal-toggle"
      />
      <dialog id={p.title} className="modal">
        <div className="modal-box border">
          <label
            htmlFor={p.title}
            onClick={() => p.onClose()}
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6 bg-base-300 stroke-neutral-content rounded-full"
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
          {p.children}
        </div>
      </dialog>
    </>
  );
};
