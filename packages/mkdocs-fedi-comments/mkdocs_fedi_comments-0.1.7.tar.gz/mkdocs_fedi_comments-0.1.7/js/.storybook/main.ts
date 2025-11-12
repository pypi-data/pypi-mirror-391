import type { StorybookConfig } from "@storybook/preact-vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: ["@storybook/addon-docs"],
  framework: {
    name: "@storybook/preact-vite",
    options: {},
  },
  staticDirs: ["../public"],
  docs: {
    //👇 See the table below for the list of supported options
    defaultName: "Documentation",
    docsMode: true,
  },
  core: {
    disableTelemetry: true, // 👈 Disables telemetry
  },
};
export default config;
