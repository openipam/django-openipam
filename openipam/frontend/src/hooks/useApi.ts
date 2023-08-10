import { HttpMethod, requestGenerator } from "../api";

export const useApi = () => {
  const api = {
    user: {
      get: requestGenerator(HttpMethod.GET, "user/"),
    },
    dns: {
      get: requestGenerator(HttpMethod.GET, "dns/"),
      create: requestGenerator(HttpMethod.POST, "dns/"),
      types: requestGenerator(HttpMethod.GET, "dns-types/"),
      veiws: requestGenerator(HttpMethod.GET, "dns-views/"),
      dhcp: requestGenerator(HttpMethod.GET, "dhcp-dns/"),
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
      mine: requestGenerator(HttpMethod.GET, "hosts/mine/"),
      attributes: requestGenerator(HttpMethod.GET, "attributes/"),
      create: requestGenerator(HttpMethod.POST, "hosts/"),
      byId(id: string) {
        return {
          get: requestGenerator(HttpMethod.GET, `hosts/${id}/`),
          update: requestGenerator(HttpMethod.PATCH, `hosts/${id}/`),
          delete: requestGenerator(HttpMethod.DELETE, `hosts/${id}/`),
          disabled: requestGenerator(HttpMethod.GET, `hosts/${id}/disabled/`),
          users: {
            get: requestGenerator(HttpMethod.GET, `hosts/${id}/users/`),
            put: requestGenerator(HttpMethod.PUT, `hosts/${id}/users/`),
            create: requestGenerator(HttpMethod.POST, `hosts/${id}/users/`),
          },
          byUser(userId: string) {
            return {
              get: requestGenerator(
                HttpMethod.GET,
                `hosts/${id}/users/${userId}/`
              ),
              update: requestGenerator(
                HttpMethod.PATCH,
                `hosts/${id}/users/${userId}/`
              ),
              delete: requestGenerator(
                HttpMethod.DELETE,
                `hosts/${id}/users/${userId}/`
              ),
            };
          },
          groups: requestGenerator(HttpMethod.GET, `hosts/${id}/groups/`),
          byGroup(groupId: string) {
            return {
              get: requestGenerator(
                HttpMethod.GET,
                `hosts/${id}/groups/${groupId}/`
              ),
              update: requestGenerator(
                HttpMethod.PATCH,
                `hosts/${id}/groups/${groupId}/`
              ),
              delete: requestGenerator(
                HttpMethod.DELETE,
                `hosts/${id}/groups/${groupId}/`
              ),
            };
          },
          attributes: requestGenerator(
            HttpMethod.GET,
            `hosts/${id}/attributes/`
          ),
          addresses: requestGenerator(HttpMethod.GET, `hosts/${id}/addresses/`),
          byAddress(addressId: string) {
            return {
              get: requestGenerator(
                HttpMethod.GET,
                `hosts/${id}/addresses/${addressId}/`
              ),
              update: requestGenerator(
                HttpMethod.PATCH,
                `hosts/${id}/addresses/${addressId}/`
              ),
              delete: requestGenerator(
                HttpMethod.DELETE,
                `hosts/${id}/addresses/${addressId}/`
              ),
            };
          },
          leases: requestGenerator(HttpMethod.GET, `hosts/${id}/leases/`),
        };
      },
    },
    logs: {
      get: requestGenerator(HttpMethod.GET, "admin/logs/"),
      getEmails: requestGenerator(HttpMethod.GET, "admin/email-logs/"),
    },
  };

  return api;
};
