import React from "react";

export const getOrdering = (columnSort: any[], map?: Map<string, string>) => {
  return columnSort
    .map((sort) => {
      const id = map?.has(sort.id) ? map.get(sort.id) : sort.id;
      if (sort.desc) {
        return `-${id}`;
      } else {
        return id;
      }
    }, [])
    .join(",");
};
