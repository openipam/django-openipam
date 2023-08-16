import React, { ReactNode, useState } from "react";
import { useAttributes } from "../../hooks/queries/useAtributes";
import { useApi } from "../../hooks/useApi";

export const AttributeModule = (p: {
  data: any[];
  showModule: boolean;
  setShowModule: (show: any) => void;
  delete?: boolean;
}) => {
  const attributes = useAttributes();
  const api = useApi();
  const [attribute, setAttribute] = useState<any[]>([
    {
      choices: null,
      name: "",
      value: "",
    },
  ]);
  const onSubmit = () => {
    attribute.forEach((a) => {
      p.data.forEach((host) => {
        return p.delete
          ? api.hosts.byId(host.mac).attributes.delete({
              [a.name]: a.name,
            })
          : api.hosts.byId(host.mac).attributes.create({
              [a.name]: a.value,
            });
      });
    });
    p.setShowModule({
      show: false,
      data: undefined,
      delete: false,
    });
  };
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
          <h1 className="text-2xl font-bold mb-4">
            {p.delete ? "Delete" : "Add"} Attributes
          </h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              onSubmit();
            }}
          >
            {attribute.map((a, i) => (
              <div key={Math.random()}>
                <label key={Math.random()} className="label">
                  Attribute
                </label>
                <select
                  id={`attribute`}
                  className="rounded-md p-2 select select-bordered max-w-md"
                  value={a.name}
                  onChange={(v) => {
                    setAttribute([
                      ...attribute.map((a, idx) => {
                        if (i === idx) {
                          return {
                            choices: attributes.data?.attributes.filter(
                              (a: any) => a.name === v.target.value
                            )[0].choices,
                            name: v.target.value,
                            value: "",
                          };
                        }
                        return a;
                      }),
                    ]);
                  }}
                >
                  {attributes.data?.attributes.map(
                    ({ name, description }: any) => (
                      <option value={name} key={Math.random()}>
                        {description}
                      </option>
                    )
                  )}
                </select>
                <label className="label">Value</label>
                {a?.choices?.length ? (
                  <>
                    <select
                      id={`attribute-choices`}
                      className="rounded-md p-2 select select-bordered max-w-md"
                      value={a.value}
                      key={Math.random()}
                      onChange={(v) => {
                        setAttribute([
                          ...attribute.map((a) => {
                            if (a.name === a.name) {
                              return {
                                ...a,
                                value: v.target.value,
                              };
                            }
                            return a;
                          }),
                        ]);
                      }}
                    >
                      {a.choices.map(({ value }: any) => (
                        <option value={value} key={Math.random()}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </>
                ) : (
                  <>
                    <input
                      className="input input-bordered"
                      value={a.value}
                      key={Math.random()}
                      onChange={(e) => {
                        setAttribute([
                          ...attribute.map((a, idx) => {
                            if (idx === i) {
                              return {
                                ...a,
                                value: e.target.value,
                              };
                            }
                            return a;
                          }),
                        ]);
                      }}
                    />
                  </>
                )}
              </div>
            ))}
            <button
              className="btn btn-secondary"
              onClick={() => {
                setAttribute([
                  ...attribute,
                  {
                    choices: null,
                    name: "",
                    value: "",
                  },
                ]);
              }}
              type="button"
            >
              Add Attribute
            </button>
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
              <button type="submit" className="btn btn-primary">
                Submit
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
