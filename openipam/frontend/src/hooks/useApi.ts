export const useApi = () => {
  const api = {
    dns: {
      get: requestGenerator("GET", "dns/"),
      create: requestGenerator("POST", "dns/"),
      byId(id: string) {
        return {
          get: requestGenerator("GET", `dns/${id}/`),
          update: requestGenerator("PUT", `dns/${id}/`),
          delete: requestGenerator("DELETE", `dns/${id}/`),
        };
      },
    },
    domains: {
      get: requestGenerator("GET", "domains/"),
      create: requestGenerator("POST", "domains/"),
      byId(id: string) {
        return {
          get: requestGenerator("GET", `domains/${id}/`),
          update: requestGenerator("PATCH", `domains/${id}/`),
          delete: requestGenerator("DELETE", `domains/${id}/`),
          createDns: requestGenerator("POST", `domains/${id}/`),
        };
      },
    },
  };

  return api;
};

const requestGenerator = (method: string, url: string) => {
  const authHeader = {
    Authorization: "Bearer " + localStorage.getItem("token"),
  };
  const baseUrl = "http://localhost:8000/api/v2/";
  switch (method) {
    case "DELETE":
    case "GET":
      return async function (params: any) {
        url = url + "?" + new URLSearchParams(params).toString();
        const response = await fetch(baseUrl + url, {
          method,
          headers: {
            "Content-Type": "application/json",
            ...authHeader,
          },
        });
        return response.json();
      };
    default:
      return async function (data: any) {
        const response = await fetch(baseUrl + url, {
          method,
          headers: {
            "Content-Type": "application/json",
            ...authHeader,
          },
          body: JSON.stringify(data),
        });

        return response.json();
      };
  }
};
