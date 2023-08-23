import React, { InputHTMLAttributes, useEffect, useRef } from "react";

export const BooleanRender = (p: { getValue: () => any }) => {
  return (
    <div className="text-center">
      <input
        type="checkbox"
        className="checkbox checkbox-sm cursor-not-allowed border-primary-content"
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
  const { indeterminate, ...rest } = p;
  return (
    <input
      type="checkbox"
      className="checkbox checkbox-sm border-primary-content border-opacity-50"
      ref={ref}
      {...rest}
    />
  );
};
