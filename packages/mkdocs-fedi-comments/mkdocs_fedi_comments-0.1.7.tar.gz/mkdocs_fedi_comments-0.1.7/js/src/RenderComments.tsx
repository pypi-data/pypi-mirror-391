import type { CommentData, CommentsResponse } from "@bovine/comments-api";
import { SimpleNote } from "@bovine/mucked-up-components";
import { orderByParents, type Ordered } from "./tree";

type RenderCommentsProps = {
  commentData: CommentsResponse;
};

type RenderChildrenProps = {
  children: CommentData[];
  ordered: Ordered;
  style?: object;
};

interface RenderWithChildrenProps {
  data: CommentData;
  ordered: Ordered;
}

function RenderChildren({ children, ordered, style }: RenderChildrenProps) {
  return (
    <div style={{ ...style }}>
      {children.map((x) => {
        return (
          <RenderWithChildren data={x} ordered={ordered} key={x.metaInfo.id} />
        );
      })}
    </div>
  );
}

function RenderWithChildren({ data, ordered }: RenderWithChildrenProps) {
  const children = ordered?.[data.metaInfo.id];
  if (!children) {
    return <SimpleNote data={data} />;
  }
  return (
    <>
      <SimpleNote data={data} />
      <RenderChildren
        children={children}
        ordered={ordered}
        style={{ marginLeft: "50px" }}
      />
    </>
  );
}

function RenderComments({ commentData }: RenderCommentsProps) {
  const ordered = orderByParents(commentData.comments);

  return (
    <div style={{ lineHeight: 1 }}>
      <RenderChildren
        children={ordered[commentData.rootUri]}
        ordered={ordered}
      />
    </div>
  );
}

export default RenderComments;
