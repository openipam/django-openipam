import React from "react";

export const IdToName = (id: string) => {
  return id
    .split("_")
    .map((word) => capitalizeWord(word))
    .join(" ");
};

const capitalizeWord = (word: string) => {
  return word.charAt(0).toUpperCase() + word.slice(1);
};
