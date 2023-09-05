import React from "react";

export const getExpiresDateFromFilter = (
  filterValue: string | undefined
): {
  expires__lt?: string;
  expires__gt?: string;
} => {
  //values are 'Expired, 1 day left, 7 days left, 30 days left, all'
  switch (filterValue) {
    case "Expired":
      return {
        expires__lt: new Date().toISOString().split("T")[0],
      };
    case "1 Day Left":
      return {
        expires__lt: new Date(new Date().setDate(new Date().getDate() + 1))
          .toISOString()
          .split("T")[0],
        expires__gt: new Date().toISOString().split("T")[0],
      };
    case "7 Days Left":
      return {
        expires__lt: new Date(new Date().setDate(new Date().getDate() + 7))
          .toISOString()
          .split("T")[0],
        expires__gt: new Date().toISOString().split("T")[0],
      };
    case "30 Days Left":
      return {
        expires__lt: new Date(new Date().setDate(new Date().getDate() + 30))
          .toISOString()
          .split("T")[0],
        expires__gt: new Date().toISOString().split("T")[0],
      };
    case "Unexpired":
      return {
        expires__gt: new Date().toISOString().split("T")[0],
      };
    default:
      return {};
  }
};
