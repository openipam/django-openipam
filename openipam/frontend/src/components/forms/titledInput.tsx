import React from "react";

export const TitledInput = (p: {
  title: string;
  onChange: (value: string) => void;
  value: string;
  type?: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  error?: string;
  props?: any;
}) => {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={p.title}>{p.title}</label>
      <input
        type={p.type ?? "text"}
        className={`input input-primary input-bordered ${p.className}`}
        placeholder={p.placeholder}
        value={p.value}
        onChange={(e) => {
          p.onChange(e.target.value);
        }}
        disabled={p.disabled}
        {...p.props}
      />
      {p.error && <p className="text-error">{p.error}</p>}
    </div>
  );
};

export const TitledTextArea = (p: {
  title: string;
  onChange: (value: string) => void;
  value: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  props?: any;
}) => {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={p.title}>{p.title}</label>
      <textarea
        className={`input input-primary input-bordered ${p.className}`}
        placeholder={p.placeholder}
        value={p.value}
        onChange={(e) => {
          p.onChange(e.target.value);
        }}
        disabled={p.disabled}
        {...p.props}
      />
    </div>
  );
};

export const TitledSelect = (p: {
  title: string;
  onChange: (value: string) => void;
  value: string;
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
  props?: any;
}) => {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={p.title}>{p.title}</label>
      <select
        className={`select select-primary select-bordered ${p.className}`}
        value={p.value}
        onChange={(e) => {
          p.onChange(e.target.value);
        }}
        disabled={p.disabled}
        {...p.props}
      >
        {p.children}
      </select>
    </div>
  );
};

export const TitledToggle = (p: {
  title: string;
  off: string;
  on: string;
  onChange: (value: boolean) => void;
  value: boolean;
  className?: string;
  disabled?: boolean;
  props?: any;
}) => {
  return (
    <div className="flex flex-col gap-2 mt-2">
      <label htmlFor={p.title}>{p.title}</label>
      <div className="flex flex-row w-full m-auto justify-center gap-1">
        <label>{p.off}</label>
        <input
          type="checkbox"
          className={`toggle toggle-primary mx-8 mt-1 ${p.className}`}
          checked={p.value}
          value={p.value ?? ""}
          onChange={(e) => {
            p.onChange(e.target.checked);
          }}
          disabled={p.disabled}
          {...p.props}
        />
        <label>{p.on}</label>
      </div>
    </div>
  );
};
