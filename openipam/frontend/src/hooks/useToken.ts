import Cookies from "js-cookie";

export const useToken = () => {
  return Cookies.get("csrftoken");
};
