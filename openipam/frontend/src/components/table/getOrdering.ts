import React from "react";

export const getOrdering = (columnSort: any[]) => {
  return columnSort
    .map((sort) => {
      if (sort.desc) {
        return `-${sort.id}`;
      } else {
        return sort.id;
      }
    }, [])
    .join(",");
};
