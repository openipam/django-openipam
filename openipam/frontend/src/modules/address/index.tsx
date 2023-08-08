import React from "react";
import { useParams } from "react-router";

export const Address = () => {
  const { address } = useParams<{ address: string }>();
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{address}</h1>
      <p>Display address details.</p>
      <p>
        DNS Records: List of DNS records associated with the IP address (A
        records, PTR records, etc.). User Permissions and Access: Who has access
        to modify or manage this IP address. Any access restrictions or special
        permissions. Security Information: Any security-related notes or
        configurations associated with the IP address. Custom Fields and Tags:
        Any additional metadata or tags that help categorize or describe the IP
        address. Actions and Management: Options to edit, modify, release, or
        reserve the IP address. Buttons to create or modify associated DNS
        records. Historical Changes: Log of changes made to the IP address,
        including modification dates, and the user who made the changes. Alerts
        and Notifications: Any alerts or notifications related to the IP address
        (e.g., DHCP lease expiration). Reporting and Analytics: Graphs or
        visualizations showing IP address usage over time. Historical data and
        trends.
      </p>
    </div>
  );
};
