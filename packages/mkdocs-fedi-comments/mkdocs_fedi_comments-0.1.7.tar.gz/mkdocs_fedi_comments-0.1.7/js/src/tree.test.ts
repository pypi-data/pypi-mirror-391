import { expect, test } from "vitest";
import { orderByParents } from "./tree";

const data = {
  content: "<p>First to comment!</p>\n",
  actorInfo: {
    id: "https://mymath.rocks/endpoints/SYn3cl_N4HAPfPHgo2x37XunLEmhV9LnxCggcYwyec0",
    avatarUrl: "https://mymath.rocks/static/profile.png",
    name: "Helge",
    identifier: "acct:helge@mymath.rocks",
    htmlUrl: "https://mymath.rocks/timeline/",
  },
  metaInfo: {
    id: "https://mymath.rocks/objects/9e4d6fd5-f590-4f25-bc72-94e3a16718e4",
    htmlUrl: null,
    published: "2025-10-14T07:07:22.708000Z",
    updated: null,
  },
  replyOf:
    "https://comments.bovine.social/pages/aHR0cHM6Ly9oZWxnZS5jb2RlYmVyZy5wYWdlL2NvbW1lbnRzLzEzNmMvZmVwLTEzNmMv",
};

test("order by parents", () => {
  const childA = { ...data, replyOf: "a" };
  const childB = { ...data, replyOf: "b" };
  const childA2 = { ...data, replyOf: "a" };

  expect(orderByParents([])).toEqual({});
  expect(orderByParents([childA])).toEqual({ a: [childA] });
  expect(orderByParents([childA, childB])).toEqual({
    a: [childA],
    b: [childB],
  });
  expect(orderByParents([childA, childA2])).toEqual({ a: [childA, childA2] });
});
