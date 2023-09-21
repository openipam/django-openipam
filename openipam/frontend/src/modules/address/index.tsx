import React, { useEffect } from "react";
import { useParams } from "react-router";
import { useApi } from "../../hooks/useApi";
import { Tab } from "../../components/tabs";
import { Address as AddressType } from "../../utils/types";
import { EditAddressModule } from "../network/editAddressModule";

export const Address = () => {
  const { address } = useParams<{ address: string }>();
  const api = useApi();
  const [edit, setEdit] = React.useState<{
    show: boolean;
    address: AddressType | undefined;
  }>({
    show: false,
    address: undefined,
  });
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
    <div className="m-4 flex flex-col gap-2 items-center justify-center">
      <h1 className="text-4xl">{address}</h1>
      <Tab
        tab={""}
        name={""}
        props={"m-2 pt-4"}
        data={addressInfo}
        edit={setEdit}
        labels={{
          network: "Network:",
          gateway: "Gateway:",
          host: "Host:",
          hostname: "Hostname:",
          pool: "Pool:",
          reserved: "Reserved:",
          last_seen: "Last Seen:",
          last_mac_seen: "Last Mac Seen:",
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
                  className="btn btn-ghost btn-outline "
                >
                  {addressInfo?.host}
                </a>
              )}
            </>
          ),
          network: (
            <a
              href={`/ui/#/networks/${addressInfo?.network}`}
              className="btn btn-ghost btn-outline "
            >
              {addressInfo?.network}
            </a>
          ),
          last_seen: addressInfo?.last_seen
            ? new Date(addressInfo.last_seen).toISOString().split("T")[0]
            : "",
          last_mac_seen: addressInfo?.last_mac_seen
            ? new Date(addressInfo.last_mac_seen).toISOString().split("T")[0]
            : "",
        }}
      />
      <EditAddressModule
        show={edit.show}
        setShow={setEdit}
        address={addressInfo}
      />
    </div>
  );
};
