import React, { useEffect, useState } from "react";
import { useAttributes } from "../hooks/queries/useAtributes";
import { useApi } from "../hooks/useApi";

export const Attributes = (p: {
  attributes: {
    [key: string]: string;
  };
  mac: string;
  owner: boolean;
}) => {
  const api = useApi();
  const attributes = useAttributes({});
  const [edit, setEdit] = useState<boolean>(false);
  const [newAttributes, setNewAttributes] = useState<any>();
  useEffect(() => {
    setNewAttributes(p.attributes);
  }, [p.attributes]);

  const onSubmit = async () => {
    const results = await api.hosts.byId(p.mac).update({
      attributes: newAttributes,
    });
    alert("TODO: submitted");
  };

  return (
    <div className={`card w-[80%] relative md:w-[50rem] bg-base-300 shadow-xl`}>
      <div className="card-body">
        <h2 className="card-title">Attributes</h2>
        {p.attributes && !edit && (
          <div className="flex flex-col gap-2">
            {Object.entries(p.attributes ?? {}).map(([key, value]) => (
              <div className="flex flex-col gap-2" key={key}>
                <label
                  htmlFor={`host-${key}`}
                  className="font-semibold mt-2 mb-0 pb-0"
                >
                  {key.toUpperCase()}
                </label>
                <input
                  type="text"
                  id={`host-${key}`}
                  value={value}
                  disabled
                  onChange={() => {}}
                  className="border border-primary-content rounded-md p-2"
                />
              </div>
            ))}
          </div>
        )}
        {p.attributes && edit && (
          <div className="flex flex-col gap-2">
            {attributes.data?.attributes.map(
              ({
                name,
                description,
                choices,
              }: {
                name: string;
                description: string;
                choices: {
                  [key: string]: string;
                }[];
              }) => (
                <div className="flex flex-col gap-2" key={name}>
                  <label
                    htmlFor={`host-${name}`}
                    className="font-semibold mt-2 mb-0 pb-0"
                  >
                    {name.toUpperCase()}
                  </label>
                  <label htmlFor={`host-${name}`} className="text-sm m-0 p-0">
                    {description}
                  </label>
                  {!choices?.length && (
                    <input
                      type="text"
                      id={`host-${name}`}
                      value={newAttributes[name] ?? ""}
                      onChange={(v) => {
                        setNewAttributes({
                          ...newAttributes,
                          [name]: v.target.value,
                        });
                      }}
                      className="rounded-md p-2 input input-bordered"
                    />
                  )}
                  {choices?.length && (
                    <select
                      id={`host-${name}`}
                      value={newAttributes[name] ?? ""}
                      onChange={(v) => {
                        setNewAttributes({
                          ...newAttributes,
                          [name]: v.target.value,
                        });
                      }}
                      className="rounded-md p-2 select select-bordered"
                    >
                      {choices.map((choice) => (
                        <option value={choice.value} key={choice.value}>
                          {choice.value}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )
            )}
          </div>
        )}
        {p.owner && (
          <div className="flex flex-row gap-2">
            <button
              className="btn btn-primary btn-md text-primary-content"
              onClick={() => {
                if (edit) {
                  onSubmit();
                }
                setEdit(!edit);
              }}
            >
              {edit ? "Save" : "Edit"}
            </button>
            {edit && (
              <button
                className="btn btn-neutral text-neutral-content btn-md"
                onClick={() => setEdit(!edit)}
              >
                Cancel
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
