import React, { useEffect, useMemo, useState } from "react";
import { AutocompleteMultiSelect, AutocompleteSelect } from "./autocomplete";
import { useGroups } from "../../hooks/queries/useGroups";

export const MultiGroupAutocomplete = (p: {
  onGroupChange: (Group: any) => void;
  groupId?: any;
}) => {
  const [filter, setFilter] = useState("");
  const GroupList = useGroups({ name: filter });

  const Groups = useMemo<any[]>(() => {
    if (!GroupList.data) {
      return [];
    }
    return GroupList.data.pages.flatMap((page) => page.groups);
  }, [GroupList.data]);

  const [Group, setGroup] = useState<any[]>([]);

  useEffect(() => {
    p.onGroupChange(Group);
  }, [Group]);

  useEffect(() => {
    if (!p.groupId) {
      setGroup([]);
      setFilter("");
      return;
    }
    const Group = Groups.find((n) => n.id === p.groupId);
    if (Group) {
      setGroup(Group);
    }
  }, [p.groupId]);

  return (
    <div className="flex flex-col">
      <label className="label">Groups</label>
      <input className="hidden" value={Group.map((g) => g.name)} disabled />
      <div className="flex flex-row overflow-x-scroll gap-1 mb-1">
        {Group.map((g) => (
          <button
            key={g.id}
            className="text-xs btn btn-xs btn-outline btn-ghost"
            onClick={() => {
              setGroup((prev) => prev.filter((p) => p.id !== g.id));
            }}
          >
            {g.name}
          </button>
        ))}
      </div>
      <AutocompleteMultiSelect
        options={Groups}
        getValueFromOption={(option) => (option ? option.name : "")}
        value={Group}
        setValue={setGroup}
        textFilter={filter}
        setTextFilter={setFilter}
        loading={GroupList.isFetching}
      />
    </div>
  );
};

export const GroupAutocomplete = (p: {
  onGroupChange: (Group: any) => void;
  groupId?: any;
  small?: boolean;
}) => {
  const [filter, setFilter] = useState("");
  const GroupList = useGroups({ name: filter });

  const Groups = useMemo<any[]>(() => {
    if (!GroupList.data) {
      return [];
    }
    return GroupList.data.pages.flatMap((page) => page.groups);
  }, [GroupList.data]);

  const [Group, setGroup] = useState<string | undefined>();

  useEffect(() => {
    p.onGroupChange(Group);
  }, [Group]);

  useEffect(() => {
    if (!p.groupId) {
      setGroup(undefined);
      setFilter("");
      return;
    }
    const Group = Groups.find((n) => n.id === p.groupId);
    if (Group) {
      setGroup(Group);
    }
  }, [p.groupId]);

  return (
    <div className="flex flex-col">
      <AutocompleteSelect
        options={Groups}
        getValueFromOption={(option) => (option ? option.name : "")}
        value={Group}
        setValue={setGroup}
        textFilter={filter}
        setTextFilter={setFilter}
        loading={GroupList.isFetching}
        small={p.small}
      />
    </div>
  );
};
