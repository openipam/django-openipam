import React, { ReactNode, useState } from "react";
import { useAttributes } from "../../hooks/queries/useAtributes";
import { useApi } from "../../hooks/useApi";
import { Module } from "../../components/forms/module";
import { FormFooter } from "../../components/forms/footer";

export const AttributeModule = (p: {
  data: any[];
  showModule: boolean;
  setShowModule: (show: any) => void;
  delete?: boolean;
}) => {
  const attributes = useAttributes({});
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
    <Module
      form
      title={`${p.delete ? "Delete" : "Add"}
      Attributes`}
      showModule={p.showModule}
      onClose={() => {
        p.setShowModule({
          show: false,
          DnsData: undefined,
        });
      }}
    >
      {attribute.map((a, i) => (
        <div key={Math.random()}>
          <label key={Math.random()} className="label">
            Attribute
          </label>
          <select
            id={`attribute`}
            className="rounded-md p-2 select select-primary select-bordered max-w-md"
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
            {attributes.data?.attributes.map(({ name, description }: any) => (
              <option value={name} key={Math.random()}>
                {description}
              </option>
            ))}
          </select>
          <label className="label">Value</label>
          {a?.choices?.length ? (
            <>
              <select
                id={`attribute-choices`}
                className="rounded-md p-2 select select-primary select-bordered max-w-md"
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
                className="input input-bordered imput-primary"
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
        className="btn btn-secondary text-secondary-content"
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
      <FormFooter
        onCancel={() =>
          p.setShowModule({
            show: false,
            data: undefined,
          })
        }
        onSubmit={onSubmit}
      />
    </Module>
  );
};
