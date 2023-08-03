import { HttpMethod, requestGenerator } from "../api";

export const useApi = () => {
  const api = {
    dns: {
      get: requestGenerator(HttpMethod.GET, "dns/"),
      create: requestGenerator(HttpMethod.POST, "dns/"),
      byId(id: number) {
        return {
          get: requestGenerator(HttpMethod.GET, `dns/${id}/`),
          update: requestGenerator(HttpMethod.PATCH, `dns/${id}/`),
          delete: requestGenerator(HttpMethod.DELETE, `dns/${id}/`),
        };
      },
    },
    domains: {
      get: requestGenerator(HttpMethod.GET, "domains/"),
      create: requestGenerator(HttpMethod.POST, "domains/"),
      byId(id: string) {
        return {
          get: requestGenerator(HttpMethod.GET, `domains/${id}/`),
          update: requestGenerator(HttpMethod.PATCH, `domains/${id}/`),
          delete: requestGenerator(HttpMethod.DELETE, `domains/${id}/`),
          dns: {
            get: requestGenerator(HttpMethod.GET, `domains/${id}/records/`),
            create: requestGenerator(HttpMethod.POST, `domains/${id}/records/`),
            byId(dnsId: string) {
              return {
                get: requestGenerator(HttpMethod.GET, `dns/${dnsId}/`),
                update: requestGenerator(HttpMethod.PATCH, `dns/${dnsId}/`),
                delete: requestGenerator(HttpMethod.DELETE, `dns/${dnsId}/`),
              };
            },
          },
        };
      },
    },
    hosts: {
      get: requestGenerator(HttpMethod.GET, "hosts/"),
      create: requestGenerator(HttpMethod.POST, "hosts/"),
      byId(id: string) {
        return {
          get: requestGenerator(HttpMethod.GET, `hosts/${id}/`),
          update: requestGenerator(HttpMethod.PATCH, `hosts/${id}/`),
          delete: requestGenerator(HttpMethod.DELETE, `hosts/${id}/`),
        };
      },
    },
  };

  return api;
};
