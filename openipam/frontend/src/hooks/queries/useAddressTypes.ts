import { useQuery } from "@tanstack/react-query";
import { useApi } from "../useApi";
import { AddressType } from "../../utils/types";

export const useAddressTypes = () => {
  const api = useApi();
  const query = useQuery({
    queryKey: ["AddressTypes"],
    queryFn: async () => {
      const results = await api.addresses.types();
      if (results.detail) {
        return {
          addressTypes: [],
        };
      }
      return {
        addressTypes: (results ?? []) as AddressType[],
      };
    },
  });

  return query;
};
