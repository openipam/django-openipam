const BASE_URL = "/api/v2";

export enum HttpMethod {
  GET = "GET",
  POST = "POST",
  PUT = "PUT",
  DELETE = "DELETE",
  PATCH = "PATCH",
}

// Auth headers are not needed. The browser will automatically send
// the session id and csrf token, which django stores in cookies.

export function requestGenerator(method: string, url: string) {
  url = `${BASE_URL}/${url}`;
  switch (method) {
    case "GET":
      return async (params?: { [key: string]: any }) => {
        const query = new URLSearchParams(params ?? {}).toString();
        const response = await fetch(`${url}?${query}`);
        // Return the JSON promise directly, rather than awaiting it.
        // This allows the caller to decide how to handle errors, and
        // also to not parse the data if they don't need it.
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
