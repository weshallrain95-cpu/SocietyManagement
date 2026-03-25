import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { SocietyProvider } from "./context/SocietyContext";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SocietyProvider>
      <App />
    </SocietyProvider>
  </React.StrictMode>
);
