import Main from "./Main";
import { createRoot } from "react-dom/client";

const appDiv = document.getElementById("app");
const root = createRoot(appDiv);
root.render(Main());
