import React from "react";
import { createRoot } from "react-dom/client";
import { HandyAppIcon, HandyLogo } from "../src/components/icons/HandyMark";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Brand preview root is missing");
}

createRoot(root).render(
  <main className="canvas">
    <section className="panel" id="app-icon">
      <HandyAppIcon size={192} />
    </section>
    <section className="panel">
      <div className="brand" id="name-lockup">
        <HandyLogo iconSize={26} wordmark="name" />
      </div>
    </section>
    <section className="panel dark">
      <div className="brand" id="numeric-lockup">
        <HandyLogo iconSize={52} wordmark="numeric" />
      </div>
    </section>
  </main>,
);

requestAnimationFrame(() => {
  document.documentElement.dataset.brandReady = "true";
});
