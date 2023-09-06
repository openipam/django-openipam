import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import Papa from "papaparse";

export const AddByCSVModule = (p: {
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const addressTypes = useAddressTypes().data?.addressTypes;
  const [headers, setHeaders] = useState<string[]>([]);
  const [hosts, dispatch] = useReducer(hostsReducer, []);
  const [loaded, setLoaded] = useState(false);
  const [data, setData] = useState<any>();
  useEffect(() => {
    console.log({ hosts });
    console.log({ data });
  }, [hosts, data]);
  const addHosts = async () => {
    await Promise.all(hosts.map((host) => api.hosts.create(host)));
    p.setShowModule(false);
  };
  const handleFileChange = (e: any) => {
    Papa.parse(e.target.files[0], {
      complete: function (results: { data: string[][] }) {
        setData(results.data);
        const headers = results.data[0].map((h) => {
          return h.toLowerCase().replace(" ", "_");
        });
        console.log({ headers });
        setHeaders(headers);
        results.data
          .filter((h, i) => h.length > 1 && i !== 0)
          .map((host: string[], i: number) => {
            dispatch({ type: "addHost", index: i, payload: {} });
            console.log("adding host");
            host.forEach((column: string, idx: number) => {
              dispatch({
                type: headers[idx],
                payload: column.replace('"', ""),
                index: i,
              });
            });
          });
        setLoaded(true);
      },
    });
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-host-module"
        className="modal-toggle"
      />
      <dialog id="add-host-module" className="modal">
        <div className="modal-box bg-base-100 border border-neutral-content max-w-full flex flex-col justify-center">
          <label
            htmlFor="add-host-module"
            onClick={() => p.setShowModule(false)}
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6"
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
          <h1 className="flex text-2xl font-bold mb-4">Upload Hosts By CSV</h1>
          <input
            type="file"
            onInput={handleFileChange}
            className="flex file-input file-input-primary"
          />
          <table className="table">
            <thead>
              <tr>{loaded && headers.map((h) => <th key={h}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {loaded &&
                hosts.map(
                  (host: { [key: string]: string | number }, i: number) => (
                    <tr key={i}>
                      {Object.values(host).map(
                        (value: string | number, idx: number) => (
                          <td key={idx} className="p-1 border border-primary">
                            <pre>{value}</pre>
                          </td>
                        )
                      )}
                    </tr>
                  )
                )}
            </tbody>
          </table>
          {loaded && (
            <button className="btn btn-primary m-4 flex" onClick={addHosts}>
              Add Hosts
            </button>
          )}
        </div>
      </dialog>
    </>
  );
};

const hostsReducer = (
  state: Host[],
  action: {
    type: string;
    payload: any;
    index: number;
  }
) => {
  switch (action.type) {
    case "addHost":
      return [...state, action.payload];
    case "removeHost":
      return state.filter((_, i) => i !== action.index);
    default:
      return state.map((h, i) => {
        if (i === action.index) {
          return hostReducer(h, action);
        } else {
          return h;
        }
      });
  }
};
const hostReducer = (state: any, action: any) => {
  let error;
  switch (action.type) {
    case "mac":
      const regex = `^([0-9a-fA-F]{2}[:.-]?){5}[0-9a-fA-F]{2}`;
      if (!action.payload.toLowerCase().match(regex)) {
        console.log({ action });
        error = "Invalid MAC Address";
      } else {
        error = undefined;
      }
      return { ...state, mac: error ? error : action.payload };
    case "hostname":
      return { ...state, hostname: action.payload };
    case "address_type":
      return {
        ...state,
        address_type: action.payload,
        network: null,
        ip_address: null,
      };
    case "description":
      return { ...state, description: action.payload };
    case "expire_days":
      return { ...state, expire_days: action.payload };
    case "network":
      return { ...state, network: action.payload };
    case "ip_address":
      return { ...state, ip_address: action.payload };
    case "dhcp_group":
      return { ...state, dhcp_group: action.payload };
    default:
      return state;
  }
};
