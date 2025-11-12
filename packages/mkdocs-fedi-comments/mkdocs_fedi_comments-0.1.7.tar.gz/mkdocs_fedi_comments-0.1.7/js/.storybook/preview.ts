import type { Preview } from "@storybook/preact-vite";
import { initialize, mswLoader } from "msw-storybook-addon";
let options = {};
if (location.hostname === "bovine.codeberg.page") {
  options = {
    serviceWorker: {
      url: "/mkdocs_fedi_comments/@storybook/mockServiceWorker.js",
    },
  };
}
initialize(options);

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  tags: ["autodocs"],
  loaders: [mswLoader],
};

export default preview;
