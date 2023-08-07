import React, { InputHTMLAttributes, useEffect, useRef } from "react";

export const BooleanRender = (p: { getValue: () => any }) => {
  return (
    <div className="text-center">
      <input
        type="checkbox"
        className="checkbox checkbox-sm cursor-not-allowed"
        checked={p.getValue() === "Y"}
        readOnly
      />
    </div>
  );
};

export function booleanAccessor<T extends object>(field: keyof T) {
  return (row: T) => (row[field] ? "Y" : "N");
}

export const PlainIndeterminateCheckbox = (
  p: {
    indeterminate?: boolean;
  } & InputHTMLAttributes<HTMLInputElement>
) => {
  const ref = useRef<HTMLInputElement>(null!);
  useEffect(() => {
    if (typeof p.indeterminate === "boolean") {
      ref.current.indeterminate = !p.checked && p.indeterminate;
    }
  }, [ref, p.indeterminate]);
  return (
    <input type="checkbox" className="checkbox checkbox-sm" ref={ref} {...p} />
  );
};
