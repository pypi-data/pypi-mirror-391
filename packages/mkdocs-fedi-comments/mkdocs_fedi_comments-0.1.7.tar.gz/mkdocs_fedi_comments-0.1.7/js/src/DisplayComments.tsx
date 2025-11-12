import { client } from "@bovine/comments-api/client";
import { comments, type CommentsResponse } from "@bovine/comments-api";
import { useEffect, useState } from "react";
import RenderComments from "./RenderComments";

type DisplayCommentsProps = {
  baseUrl: string;
  encodedUrl: string;
};

function DisplayComments({ baseUrl, encodedUrl }: DisplayCommentsProps) {
  const [commentData, setCommentData] = useState<CommentsResponse | null>(null);
  const [loading, setLoading] = useState("loading");

  client.setConfig({
    baseUrl: baseUrl,
  });

  useEffect(() => {
    const loadComments = async () => {
      const result = await comments({
        path: {
          path: encodedUrl,
        },
      });

      const responseStatus = result.response.status;

      if (responseStatus == 200 && result.data) {
        if (result.data.comments.length == 0) {
          setLoading("noData");
        } else {
          setCommentData(result.data);
          setLoading("success");
        }
      } else if (responseStatus == 404) {
        setLoading("noData");
      }
    };
    loadComments();
  }, [baseUrl, encodedUrl]);

  if (loading == "loading") {
    return <>Loading Comments</>;
  }

  if (loading === "noData") {
    return <>No comments</>;
  }

  if (loading !== "success" || commentData == null) {
    return <>Something went wrong</>;
  }

  return <RenderComments commentData={commentData} />;
}

export default DisplayComments;
