export const useApi = () => {
  return {
    user: {
      get: requestGenerator(HttpMethod.GET, "users/"),
      me: requestGenerator(HttpMethod.GET, "users/me/"),
      byId(id: string) {
        return {
          get: requestGenerator(HttpMethod.GET, `users/${id}/`),
        };
      },
    },
    dns: {
      get: requestGenerator(HttpMethod.GET, "dns/"),
      create: requestGenerator(HttpMethod.POST, "dns/"),
      types: requestGenerator(HttpMethod.GET, "dns-types/"),
      veiws: requestGenerator(HttpMethod.GET, "dns-views/"),
      dhcp: requestGenerator(HttpMethod.GET, "dns/dhcp"),
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
          dhcp: {
            get: requestGenerator(HttpMethod.GET, `domains/${id}/dhcp/`),
            create: requestGenerator(HttpMethod.POST, `domains/${id}/dhcp/`),
            // byId(dhcpId: string) {
            //   return {
            //     get: requestGenerator(HttpMethod.GET, `dhcp/${dhcpId}/`),
            //     update: requestGenerator(HttpMethod.PATCH, `dhcp/${dhcpId}/`),
            //     delete: requestGenerator(HttpMethod.DELETE, `dhcp/${dhcpId}/`),
            //   };
            // }
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
          disable: requestGenerator(HttpMethod.POST, `hosts/${id}/disabled/`),
          enable: requestGenerator(HttpMethod.DELETE, `hosts/${id}/disabled/`),
          populateDns: requestGenerator(
            HttpMethod.POST,
            `hosts/${id}/populateDns/`
          ),
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
          groups: {
            get: requestGenerator(HttpMethod.GET, `hosts/${id}/groups/`),
            put: requestGenerator(HttpMethod.PUT, `hosts/${id}/groups/`),
            create: requestGenerator(HttpMethod.POST, `hosts/${id}/groups/`),
          },
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
          attributes: {
            get: requestGenerator(HttpMethod.GET, `hosts/${id}/attributes/`),
            create: requestGenerator(
              HttpMethod.POST,
              `hosts/${id}/attributes/`
            ),
            delete: requestGenerator(
              HttpMethod.DELETE,
              `hosts/${id}/attributes/`
            ),
          },
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
          dhcp: {
            set: requestGenerator(HttpMethod.POST, `hosts/${id}/dhcp/`),
            delete: requestGenerator(HttpMethod.DELETE, `hosts/${id}/dhcp/`),
          },
          setNetwork: requestGenerator(HttpMethod.POST, `hosts/${id}/network/`),
        };
      },
    },
    logs: {
      get: requestGenerator(HttpMethod.GET, "admin/logs/"),
      getEmails: requestGenerator(HttpMethod.GET, "admin/email-logs/"),
    },
    dhcpGroups: {
      get: requestGenerator(HttpMethod.GET, "dhcp-groups/"),
    },
    networks: {
      get: requestGenerator(HttpMethod.GET, "networks/"),
      byId(id: string) {
        return {
          get: requestGenerator(HttpMethod.GET, `networks/${id}/`),
          addresses: {
            get: requestGenerator(HttpMethod.GET, `networks/${id}/addresses/`),
          },
        };
      },
    },
  };
};

const BASE_URL = "/api/v2";

enum HttpMethod {
  GET = "GET",
  POST = "POST",
  PUT = "PUT",
  DELETE = "DELETE",
  PATCH = "PATCH",
}

function requestGenerator(method: string, url: string) {
  url = `${BASE_URL}/${url}`;
  switch (method) {
    case "GET":
      return async (params?: { [key: string]: any }) => {
        const query = new URLSearchParams(params ?? {}).toString();
        const response = await fetch(`${url}?${query}`);
        return response.json();
      };
    default:
      return async (data?: { [key: string]: any }) => {
        const response = await fetch(url, {
          method,
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data ?? {}),
        });
        return response.json();
      };
  }
}
