import { createRoot } from "react-dom/client";

import DisplayComments from "./DisplayComments";

export function add(elementId: string, baseUrl: string, encodedUrl: string) {
  const el = document.getElementById(elementId);
  if (!el) {
    console.error(`Element with id ${elementId} not found`);
    return;
  }
  const root = createRoot(el);
  root.render(<DisplayComments baseUrl={baseUrl} encodedUrl={encodedUrl} />);
}
