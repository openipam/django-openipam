import { useQuery } from "@tanstack/react-query";
import { useApi } from "../useApi";

export const useAttributes = () => {
  const api = useApi();
  const query = useQuery({
    queryKey: ["attributes"],
    queryFn: async () => {
      const results = await api.hosts.attributes();
      if (results.detail) {
        return {
          attributes: [],
        };
      }
      return {
        attributes: results,
      };
    },
  });

  return query;
};
