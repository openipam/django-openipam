import React, { useEffect, useMemo, useState } from "react";
import { AutocompleteSelect } from "./autocomplete";
import { Hub } from "@mui/icons-material";
import { Network } from "../../utils/types";
import { useInfiniteSharedNetworks } from "../../hooks/queries/useInfiniteSharedNetworks";

export const SharedNetworkAutocomplete = (p: {
  onNetworkChange: (network: any) => void;
  networkName?: string;
}) => {
  const [filter, setFilter] = useState("");
  const networkList = useInfiniteSharedNetworks({
    name: filter,
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
    if (!p.networkName) {
      setNetwork(undefined);
      setFilter("");
      return;
    }
    const n = networks.find((n) => n.name === p.networkName);
    if (n) {
      setNetwork(n);
    }
  }, [p.networkName]);

  return (
    <AutocompleteSelect
      options={networks}
      getValueFromOption={(option) => (option ? option.name : "")}
      value={network}
      setValue={setNetwork}
      textFilter={filter}
      setTextFilter={setFilter}
      loading={networkList.isFetching}
      icon={<Hub />}
    />
  );
};
