import React from "react";

export const Network = () => {
  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Network TODO</h1>
      <p>Allow administrators to define and manage subnets.</p>
      <p>Display network hierarchy and subnet details.</p>
      <p>Highlight IP allocation status within each subnet.</p>
      <p>On the network detail page:</p>
      <p>List and manage IP addresses within each network.</p>
      <p>
        Provide filtering and searching capabilities based on status (used,
        available, reserved), network, or domain.
      </p>
    </div>
  );
};
