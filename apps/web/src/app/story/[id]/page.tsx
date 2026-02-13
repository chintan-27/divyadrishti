"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchStory, fetchComments, type Story, type Comment } from "@/lib/api";
import SentimentPie from "@/components/SentimentPie";
import CommentTree from "@/components/CommentTree";

export default function StoryDetailPage() {
  const params = useParams<{ id: string }>();
  const [story, setStory] = useState<Story | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;

    Promise.all([fetchStory(params.id), fetchComments(params.id)])
      .then(([storyData, commentsData]) => {
        setStory(storyData);
        setComments(commentsData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-400">
        {error ?? "Story not found"}
      </div>
    );
  }

  const sentiment = story.sentiment ?? { positive: 0, negative: 0, neutral: 0 };

  return (
    <div className="space-y-8">
      {/* Story header */}
      <div>
        <h1 className="text-2xl font-bold leading-tight">{story.title}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-400">
          <span>{story.score} points</span>
          <span>by {story.by}</span>
          <span>{formatTime(story.time)}</span>
          {story.url && (
            <a
              href={story.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:text-accent-hover"
            >
              {new URL(story.url).hostname}
            </a>
          )}
        </div>
      </div>

      {/* Sentiment chart */}
      <div className="card max-w-md">
        <h2 className="mb-4 text-lg font-semibold">Sentiment Breakdown</h2>
        <SentimentPie
          positive={sentiment.positive}
          negative={sentiment.negative}
          neutral={sentiment.neutral}
        />
      </div>

      {/* Comments */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">
          Comments ({comments.length})
        </h2>
        {comments.length > 0 ? (
          <CommentTree comments={comments} />
        ) : (
          <p className="text-gray-500">No comments yet.</p>
        )}
      </div>
    </div>
  );
}

function formatTime(unix: number): string {
  const date = new Date(unix * 1000);
  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  if (diffHours < 1) return "just now";
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}
