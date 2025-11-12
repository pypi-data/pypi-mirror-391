import type { CommentData } from "@bovine/comments-api";

type Ordered = {
  [key: string]: CommentData[];
};

function orderByParents(data: Array<CommentData>) {
  const result: Ordered = {};

  for (const element of data) {
    if (!(element.replyOf in result)) {
      result[element.replyOf] = [];
    }
    result[element.replyOf].push(element);
  }

  return result;
}

export { orderByParents, type Ordered };
