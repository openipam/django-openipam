import { useQuery } from "@tanstack/react-query";
import { useApi } from "../useApi";

export const useAttributes = (p: { [key: string]: any }) => {
  const api = useApi();
  const query = useQuery({
    queryKey: ["attributes"],
    queryFn: async () => {
      const results = await api.hosts.attributes({ ...p });
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
