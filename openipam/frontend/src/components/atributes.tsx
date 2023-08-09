import React from "react";
import { useAttributes } from "../hooks/queries/useAtributes";

export const Attributes = (p: {
  attributes: {
    [key: string]: string;
  };
}) => {
  const attributes = useAttributes();
  const [edit, setEdit] = React.useState<boolean>(false);
  return (
    <div className={`card w-[80%] relative md:w-[40rem] bg-gray-600 shadow-xl`}>
      <div className="card-body">
        <h2 className="card-title">Attributes</h2>
        {p.attributes && !edit && (
          <div className="flex flex-col gap-2">
            {Object.entries(p.attributes ?? {}).map(([key, value]) => (
              <div className="flex flex-col gap-2">
                <label htmlFor={`host-${key}`}>{key}</label>
                <input
                  type="text"
                  id={`host-${key}`}
                  value={value}
                  disabled
                  onChange={() => {}}
                  className="border border-gray-300 rounded-md p-2"
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
                <div className="flex flex-col gap-2">
                  <label htmlFor={`host-${name}`}>{name}</label>
                  <input
                    type="text"
                    id={`host-${name}`}
                    value={JSON.stringify(description)}
                    onChange={() => {}}
                    className="border border-gray-300 rounded-md p-2"
                  />
                </div>
              )
            )}
          </div>
        )}
        <button
          className="btn btn-primary btn-md"
          onClick={() => setEdit(!edit)}
        >
          {edit ? "Save" : "Edit"}
        </button>
        {/* <pre>{JSON.stringify(attributes.data?.attributes, null, 2)}</pre> */}
      </div>
    </div>
  );
};

{
  /* <div className="flex flex-col gap-2">
              <label htmlFor="host-mac">Mac</label>
              <input
                type="text"
                id="host-mac"
                value={p.HostData?.mac ?? ""}
                disabled
                onChange={() => {}}
                className="border border-gray-300 rounded-md p-2"
              />
            </div> */
}
