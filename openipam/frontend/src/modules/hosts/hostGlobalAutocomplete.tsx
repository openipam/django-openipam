import React, { useEffect, useState } from "react";
import { AutocompleteSelect } from "../../components/autocomplete/autocomplete";
import { FilterAlt } from "@mui/icons-material";
import { useApi } from "../../hooks/useApi";
import { useQuery } from "@tanstack/react-query";

const useOptions = (q: { q: string }) => {
  const api = useApi();
  const query = useQuery(["autocomplete", q], () => api.autocomplete(q));
  return query.data?.results ?? [];
};

//TODO: implement AND/OR logic on filters
export const HostGlobalAutocomplete = (p: {
  onAddFilter: (filter: any) => void;
}) => {
  const [filter, setFilter] = useState("");
  const [value, setValue] = useState<any>();
  const options = useOptions({ q: filter });

  console.log(options);

  useEffect(() => {
    if (value) {
      p.onAddFilter(value);
      setFilter("");
    }
  }, [value]);

  return (
    <AutocompleteSelect
      options={options}
      getValueFromOption={(option) => {
        return option ? `${option.text}` : "";
      }}
      value={""}
      setValue={setValue}
      textFilter={filter}
      setTextFilter={setFilter}
      loading={options.isFetching}
      icon={<FilterAlt />}
      disableFilter={true}
    />
  );
};
