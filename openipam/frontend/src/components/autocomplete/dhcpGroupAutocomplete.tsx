import React, { useEffect, useMemo, useState } from "react";
import { AutocompleteSelect } from "./autocomplete";
import { useDhcpGroups } from "../../hooks/queries/useDhcpGroups";

export const DhcpAutocomplete = (p: {
  onDhcpChange: (Dhcp: any) => void;
  DhcpId?: any;
}) => {
  const [filter, setFilter] = useState("");
  const DhcpList = useDhcpGroups({ name: filter });

  const Dhcps = useMemo<any[]>(() => {
    if (!DhcpList.data) {
      return [];
    }
    return DhcpList.data.pages.flatMap((page) => page.dhcpGroups);
  }, [DhcpList.data]);

  const [Dhcp, setDhcp] = useState<String>();

  useEffect(() => {
    p.onDhcpChange(Dhcp);
  }, [Dhcp]);

  useEffect(() => {
    if (!p.DhcpId) return;
    const Dhcp = Dhcps.find((n) => n.id === p.DhcpId);
    if (Dhcp) {
      setDhcp(Dhcp);
    }
  }, [p.DhcpId]);

  return (
    <AutocompleteSelect
      options={Dhcps}
      getValueFromOption={(option) => (option ? option.name : "")}
      value={Dhcp}
      setValue={setDhcp}
      textFilter={filter}
      setTextFilter={setFilter}
      loading={DhcpList.isFetching}
    />
  );
};
