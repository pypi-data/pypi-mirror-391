import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import DisplayComments from "./DisplayComments.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <DisplayComments
      baseUrl="https://comments.bovine.social/comments"
      encodedUrl="aHR0cHM6Ly9oZWxnZS5jb2RlYmVyZy5wYWdlL21rZG9jc19mZWRpX2NvbW1lbnRzLw=="
    />
  </StrictMode>,
);
