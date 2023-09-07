import React, { useEffect, useReducer, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import Papa from "papaparse";

const exampleCSVHeaders = [
  "mac",
  "Hostname",
  "IP address",
  "network",
  "expire_days",
  "address Type",
  "description",
  "DHCP_GROUP",
];
const exampleCSV: any[] = [
  {
    mac: "11:11:11:11:11:11",
    hostname: "example.bluezone.usu.edu",
    address_type: "Management",
    ip_address: "10.21.20.2",
    description: "test example",
    expire_days: 365,
  },
  {
    mac: "11:11:11:11:11:11",
    hostname: "example.bluezone.usu.edu",
    network: "10.2.0.0/24",
    address_type: "Other",
    description: "",
    expire_days: 365,
  },
  {
    mac: "11:11:11:11:11:11",
    hostname: "example.bluezone.usu.edu",
    address_type: "Dynamic",
    description: "",
    expire_days: 365,
  },
  {
    mac: "11:11:11:11:11:11",
    hostname: "example.bluezone.usu.edu",
    address_type: "Dynamic",
    description: "",
    expire_days: 365,
  },
  {
    mac: "11:11:11:11:11:11",
    hostname: "example.bluezone.usu.edu",
    address_type: "Dynamic",
    description: "",
    expire_days: 365,
    dhcp_group: "aruba-cluster",
  },
];

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
  const addHosts = async () => {
    //todo: map address type to id, same with ip address and network
    await Promise.all(
      hosts.map((host) =>
        api.hosts.create({ ...host, expire_days: host.expire_days ?? 7 })
      )
    );
    p.setShowModule(false);
  };
  const handleFileChange = (e: any) => {
    Papa.parse(e.target.files[0], {
      complete: function (results: { data: string[][] }) {
        setData(results.data);
        const headers = results.data[0].map((h) => {
          const head = h.toLowerCase().replace(" ", "_");
          if (head.startsWith("expire")) return "expire_days";
          if (head === "address") return "ip_address";
          if (head.startsWith("mac")) return "mac";
          return head;
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
          {!loaded && (
            <div className="flex flex-col">
              <h1 className="mt-4 text-lg font-bold">Example CSV layout:</h1>
              <p className="my-1">
                Note: header name is not case or underscore sensitive. You may
                include or exclude as many columns as you want.
              </p>
              <p className="my-1">
                Only mac, hostname, and address type are required. Expire_days
                will default to 7 if left blank, and user_owner will default to
                your user if no user or group owner is given.
              </p>
              <p>
                Please double check all records to ensure addresses are valid,
                and non-dynamic types given either network or ip address, and
                that it is valid for the given address type.
              </p>
            </div>
          )}
          <table className="table">
            <thead>
              <tr>
                {loaded
                  ? headers.map((h) => <th key={h}>{h}</th>)
                  : exampleCSVHeaders.map((h) => <th key={h}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {loaded
                ? hosts.map(
                    (host: { [key: string]: string | number }, i: number) => (
                      <tr key={i}>
                        {headers.map((value: string | number, idx: number) => (
                          <td key={idx} className="p-1 border border-primary">
                            <pre>{host[value] ?? ""}</pre>
                          </td>
                        ))}
                      </tr>
                    )
                  )
                : exampleCSV.map(
                    (host: { [key: string]: string | number }, i: number) => (
                      <tr key={i}>
                        {exampleCSVHeaders
                          .map((h) => {
                            const head = h.toLowerCase().replace(" ", "_");
                            if (head.startsWith("expire")) return "expire_days";
                            if (head === "address") return "ip_address";
                            return head;
                          })
                          .map((value: string, idx: number) => (
                            <td key={idx} className="p-1 border border-primary">
                              <pre>{host[value] ?? ""}</pre>
                            </td>
                          ))}
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
