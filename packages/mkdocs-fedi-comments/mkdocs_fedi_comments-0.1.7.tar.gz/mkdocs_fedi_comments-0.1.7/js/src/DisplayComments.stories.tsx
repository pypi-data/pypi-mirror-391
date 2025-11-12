import type { Meta } from "@storybook/preact-vite";
import { http, HttpResponse, delay } from "msw";

import DisplayComments from "./DisplayComments";

const meta = {
  component: DisplayComments,
} satisfies Meta<typeof DisplayComments>;

export default meta;

const data = {
  comments: [
    {
      content:
        '<p><span><a href="https://comments.bovine.social/actor/DO3D49jJrNlpPNm-FwEEsA" class="mention" rel="noopener noreferrer">@<span>mkdocs_plugin_test</span></a></span> life testing is fun, no?</p>',
      actorInfo: {
        id: "https://mastodon.social/users/the_milkman",
        avatarUrl: null,
        name: "milkman",
        identifier: "acct:the_milkman@mastodon.social",
        htmlUrl: "https://mastodon.social/@the_milkman",
      },
      metaInfo: {
        id: "https://mastodon.social/users/the_milkman/statuses/115345671482881173",
        htmlUrl: "https://mastodon.social/@the_milkman/115345671482881173",
        published: "2025-10-09T18:41:10Z",
        updated: null,
      },
      replyOf:
        "https://comments.bovine.social/pages/aHR0cHM6Ly9oZWxnZS5jb2RlYmVyZy5wYWdlL21rZG9jc19mZWRpX2NvbW1lbnRzLw==",
    },
    {
      content:
        '<p><span><a href="https://comments.bovine.social/actor/DO3D49jJrNlpPNm-FwEEsA" class="mention" rel="noopener noreferrer">@<span>mkdocs_plugin_test</span></a></span> it should be live</p>',
      actorInfo: {
        id: "https://mastodon.social/users/the_milkman",
        avatarUrl: null,
        name: "milkman",
        identifier: "acct:the_milkman@mastodon.social",
        htmlUrl: "https://mastodon.social/@the_milkman",
      },
      metaInfo: {
        id: "https://mastodon.social/users/the_milkman/statuses/115345708248430072",
        htmlUrl: "https://mastodon.social/@the_milkman/115345708248430072",
        published: "2025-10-09T18:50:31Z",
        updated: null,
      },
      replyOf:
        "https://mastodon.social/users/the_milkman/statuses/115345671482881173",
    },
    {
      content:
        '<p><span><a href="https://comments.bovine.social/actor/DO3D49jJrNlpPNm-FwEEsA" class="mention" rel="noopener noreferrer">@<span>mkdocs_plugin_test</span></a></span> another one</p>',
      actorInfo: {
        id: "https://mastodon.social/users/the_milkman",
        avatarUrl: null,
        name: "milkman",
        identifier: "acct:the_milkman@mastodon.social",
        htmlUrl: "https://mastodon.social/@the_milkman",
      },
      metaInfo: {
        id: "https://mastodon.social/users/the_milkman/statuses/115345708813641492",
        htmlUrl: "https://mastodon.social/@the_milkman/115345708813641492",
        published: "2025-10-09T18:50:40Z",
        updated: null,
      },
      replyOf:
        "https://comments.bovine.social/pages/aHR0cHM6Ly9oZWxnZS5jb2RlYmVyZy5wYWdlL21rZG9jc19mZWRpX2NvbW1lbnRzLw==",
    },
  ],
  sharedBy: [],
  likedBy: [],
  rootUri:
    "https://comments.bovine.social/pages/aHR0cHM6Ly9oZWxnZS5jb2RlYmVyZy5wYWdlL21rZG9jc19mZWRpX2NvbW1lbnRzLw==",
};

export const FullInformation = {
  args: {
    baseUrl: "https://endpoint",
    encodedUrl: "something",
  },
  parameters: {
    msw: {
      handlers: [
        http.get("https://endpoint/something", async () => {
          await delay(800);
          return HttpResponse.json(data);
        }),
      ],
    },
  },
};
