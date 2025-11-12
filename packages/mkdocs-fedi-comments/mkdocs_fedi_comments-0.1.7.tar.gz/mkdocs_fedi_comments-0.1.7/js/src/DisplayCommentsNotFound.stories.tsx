import type { Meta } from "@storybook/preact-vite";
import { http, HttpResponse, delay } from "msw";

import DisplayComments from "./DisplayComments";

const meta = {
  component: DisplayComments,
} satisfies Meta<typeof DisplayComments>;

export default meta;

export const NotFoundError = {
  args: {
    baseUrl: "https://endpoint",
    encodedUrl: "something",
  },
  parameters: {
    msw: {
      handlers: [
        http.get("https://endpoint/something", async () => {
          await delay(800);
          return new HttpResponse(null, {
            status: 404,
          });
        }),
      ],
    },
  },
};
