import React, { useEffect } from "react";

let initialTheme = "light";
const lightThemeMq = window.matchMedia("(prefers-color-scheme: dark)");
if (lightThemeMq.matches) {
  initialTheme = "dark";
}

const htmlTage = document.getElementsByTagName("html");
if (htmlTage.length > 0) {
  htmlTage[0].setAttribute("data-theme", initialTheme);
}

export const useTheme = () => {
  const [theme, setTheme] = React.useState<string>(
    localStorage.getItem("theme") ?? initialTheme
  );

  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  return { theme, setTheme };
};

export const useThemes = () => {
  return themes;
};

const themes = [
  "light",
  "dark",
  "dracula",
  "winter",
  "night",
  "cupcake",
  "black",
  "corporate",
  "synthwave",
  "retro",
  "bumblebee",
  "emerald",
  "halloween",
  "garden",
  "forest",
  "lofi",
  "fantasy",
  "cmyk",
  "autumn",
  "lemonade",
  "valentine",
];
