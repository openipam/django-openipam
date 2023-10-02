import React from "react";

export const FormFooter = (p: {
  onCancel: () => void;
  onSubmit: () => void;
  submitText?: string;
  cancelText?: string;
  submitClassName?: string;
  cancelClassName?: string;
  submitDisabled?: boolean;
  cancelDisabled?: boolean;
}) => {
  const [loading, setLoading] = React.useState(false);
  return (
    <div className="flex justify-end gap-4 mt-4">
      <button
        className={`btn btn-neutral text-neutral-content ${p.cancelClassName}`}
        onClick={() => {
          setLoading(true);
          p.onCancel();
          setLoading(false);
        }}
        type="reset"
        disabled={p.cancelDisabled || loading}
      >
        {p.cancelText ?? "Cancel"}
      </button>
      <button
        type="submit"
        className={`btn btn-primary text-primary-content ${p.submitClassName}`}
        onClick={() => {
          setLoading(true);
          p.onSubmit();
          setLoading(false);
        }}
        disabled={p.submitDisabled || loading}
      >
        {p.submitText ?? "Submit"}
      </button>
    </div>
  );
};
