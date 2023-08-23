import { createRoot } from "react-dom/client";
import { App } from "./navigation/BrowserRouter";

let theme = "dark";
const lightThemeMq = window.matchMedia("(prefers-color-scheme: light)");
if (lightThemeMq.matches) {
  theme = "light";
} else {
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
