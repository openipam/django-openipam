import React from "react";

export const TitledInput = (p: {
  title: string;
  onChange: (value: string) => void;
  value: string;
  type?: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
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
    </div>
  );
};
