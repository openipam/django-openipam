import { createRoot } from "react-dom/client";
import { App } from "./navigation/BrowserRouter";

let theme = "light";
const lightThemeMq = window.matchMedia("(prefers-color-scheme: dark)");
if (lightThemeMq.matches) {
  theme = "dark";
}

const htmlTage = document.getElementsByTagName("html");
if (htmlTage.length > 0) {
  htmlTage[0].setAttribute("data-theme", theme);
}

const appDiv = document.getElementById("app");
if (appDiv === null) {
  throw new Error(
    "Could not find element with id 'app', is this the right template?"
  );
}
const root = createRoot(appDiv);
root.render(App());
