import React, { useEffect } from "react";
import { useParams } from "react-router";
import { useApi } from "../../hooks/useApi";
import { Tab } from "../../components/tabs";
import { Address as AddressType } from "../../utils/types";

export const Address = () => {
  const { address } = useParams<{ address: string }>();
  const api = useApi();
  const [addressInfo, setAddressInfo] = React.useState<AddressType>({} as any);
  useEffect(() => {
    if (!address) return;
    getAddressInfo();
  }, [address]);
  const getAddressInfo = async () => {
    const response = await api.addresses.byId(address!).get();
    setAddressInfo(response);
  };

  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{address}</h1>
      <Tab
        tab={""}
        name={""}
        data={addressInfo}
        labels={{
          network: "Network:",
          gateway: "Gateway:",
          host: "Host:",
          hostname: "Hostname:",
          pool: "Pool:",
          reserved: "Reserved:",
          changed: "Changed:",
        }}
        custom={{
          changed: addressInfo?.changed
            ? new Date(addressInfo.changed).toISOString().split("T")[0]
            : "",
          pool: addressInfo?.pool?.name ?? "None",
          reserved: addressInfo?.reserved ? "Yes" : "No",
          host: (
            <>
              {addressInfo?.host && (
                <a
                  href={`/ui/#/hosts/${addressInfo?.host}`}
                  className="btn btn-ghost btn-outline text-white"
                >
                  {addressInfo?.host}
                </a>
              )}
            </>
          ),
          network: (
            <a
              href={`/ui/#/networks/${addressInfo?.network}`}
              className="btn btn-ghost btn-outline text-white"
            >
              {addressInfo?.network}
            </a>
          ),
        }}
      />
    </div>
  );
};
