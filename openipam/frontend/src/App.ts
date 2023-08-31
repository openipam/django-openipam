import { createRoot } from "react-dom/client";
import { App } from "./navigation/BrowserRouter";

const appDiv = document.getElementById("app");
if (appDiv === null) {
  throw new Error(
    "Could not find element with id 'app', is this the right template?"
  );
}
const root = createRoot(appDiv);
root.render(App());
