"use client";

import type { Comment } from "@/lib/api";

interface CommentTreeProps {
  comments: Comment[];
}

export default function CommentTree({ comments }: CommentTreeProps) {
  return (
    <div className="space-y-1">
      {comments.map((comment) => (
        <CommentNode key={comment.id} comment={comment} depth={0} />
      ))}
    </div>
  );
}

interface CommentNodeProps {
  comment: Comment;
  depth: number;
}

function CommentNode({ comment, depth }: CommentNodeProps) {
  const sentimentColor = getSentimentColor(comment.sentiment_label);
  const maxDepth = 6;
  const indent = Math.min(depth, maxDepth);

  return (
    <div style={{ marginLeft: `${indent * 20}px` }}>
      <div className="group rounded-lg border border-transparent p-3 hover:border-gray-800 hover:bg-surface-overlay/50">
        {/* Header */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="font-medium text-gray-400">{comment.by}</span>
          <span>{formatTimeAgo(comment.time)}</span>
          {comment.sentiment_label && (
            <span
              className="rounded-full px-2 py-0.5 text-[10px] font-medium"
              style={{
                backgroundColor: `${sentimentColor}20`,
                color: sentimentColor,
              }}
            >
              {comment.sentiment_label}
            </span>
          )}
        </div>

        {/* Body */}
        <div
          className="mt-1 text-sm leading-relaxed text-gray-300"
          dangerouslySetInnerHTML={{ __html: comment.text ?? "" }}
        />
      </div>

      {/* Children */}
      {comment.children && comment.children.length > 0 && (
        <div className="border-l border-gray-800">
          {comment.children.map((child) => (
            <CommentNode key={child.id} comment={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function getSentimentColor(label?: string): string {
  switch (label) {
    case "positive":
      return "#22c55e";
    case "negative":
      return "#ef4444";
    case "neutral":
      return "#94a3b8";
    default:
      return "#94a3b8";
  }
}

function formatTimeAgo(unix: number): string {
  const diffMs = Date.now() - unix * 1000;
  const diffMins = Math.floor(diffMs / (1000 * 60));
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}
