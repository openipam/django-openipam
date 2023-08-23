import React, { useEffect, useMemo, useState } from "react";
import { useInfiniteNetworks } from "../../hooks/queries/useInfiniteNetworks";
import { AutocompleteSelect } from "./autocomplete";
import { Hub } from "@mui/icons-material";
import { Network } from "../../utils/types";

export const NetworkAutocomplete = (p: {
  onNetworkChange: (network: any) => void;
  networkId?: string;
  addressType?: number;
}) => {
  const [filter, setFilter] = useState("");
  const networkList = useInfiniteNetworks({
    network: filter,
    ...(p.addressType ? { address_type: p.addressType } : {}),
  });

  const networks = useMemo<any[]>(() => {
    if (!networkList.data) {
      return [];
    }
    return networkList.data.pages.flatMap((page) => page.networks);
  }, [networkList.data]);

  const [network, setNetwork] = useState<Network>();

  useEffect(() => {
    p.onNetworkChange(network);
  }, [network]);

  useEffect(() => {
    if (!p.networkId) {
      setNetwork(undefined);
      setFilter("");
      return;
    }
    const n = networks.find((n) => n.network === p.networkId);
    if (n) {
      setNetwork(n);
    }
  }, [p.networkId]);

  return (
    <AutocompleteSelect
      options={networks}
      getValueFromOption={(option) => (option ? option.network : "")}
      value={network}
      setValue={setNetwork}
      textFilter={filter}
      setTextFilter={setFilter}
      loading={networkList.isFetching}
      icon={<Hub />}
    />
  );
};
