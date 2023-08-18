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
    const response = await api.address(address!).get();
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
            <a
              href={`/ui/#/hosts/${addressInfo?.host}`}
              className="btn btn-ghost btn-outline text-white"
            >
              {addressInfo?.host}
            </a>
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
      <p>
        DNS Records: List of DNS records associated with the IP address (A
        records, PTR records, etc.).
      </p>
      <p>
        {" "}
        User Permissions and Access: Who has access to modify or manage this IP
        address. Any access restrictions or special permissions.
      </p>
      <p>
        {" "}
        Security Information: Any security-related notes or configurations
        associated with the IP address.
      </p>
      <p>
        {" "}
        Custom Fields and Tags: Any additional metadata or tags that help
        categorize or describe the IP address.
      </p>
      <p>
        {" "}
        Actions and Management: Options to edit, modify, release, or reserve the
        IP address. Buttons to create or modify associated DNS records.
      </p>
      <p>
        {" "}
        Historical Changes: Log of changes made to the IP address, including
        modification dates, and the user who made the changes.
      </p>
      <p>
        {" "}
        Alerts and Notifications: Any alerts or notifications related to the IP
        address (e.g., DHCP lease expiration).
      </p>
      <p>
        {" "}
        Reporting and Analytics: Graphs or visualizations showing IP address
        usage over time. Historical data and trends.
      </p>
    </div>
  );
};
