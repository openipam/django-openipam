import { useQuery } from "@tanstack/react-query";
import { useApi } from "./useApi";

export const useAuth = () => {
  const api = useApi();
  const query = useQuery({
    queryKey: ["auth"],
    queryFn: async () => {
      const results = await api.user.me();
      return {
        auth: results,
      };
    },
  });

  return query.data?.auth;
};
