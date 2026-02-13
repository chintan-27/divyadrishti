"use client";

import Link from "next/link";
import type { Story } from "@/lib/api";

interface StoryCardProps {
  story: Story;
}

export default function StoryCard({ story }: StoryCardProps) {
  const timeAgo = formatTimeAgo(story.time);

  return (
    <Link href={`/story/${story.id}`} className="card block">
      <h2 className="font-semibold leading-snug text-gray-100 line-clamp-2">
        {story.title}
      </h2>
      {story.url && (
        <p className="mt-1 truncate text-xs text-gray-500">
          {extractDomain(story.url)}
        </p>
      )}
      <div className="mt-3 flex items-center gap-3 text-xs text-gray-400">
        <span className="font-medium text-accent">{story.score} pts</span>
        <span>by {story.by}</span>
        <span>{timeAgo}</span>
        <span className="ml-auto">{story.descendants ?? 0} comments</span>
      </div>
    </Link>
  );
}

function extractDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function formatTimeAgo(unix: number): string {
  const diffMs = Date.now() - unix * 1000;
  const diffMins = Math.floor(diffMs / (1000 * 60));
  if (diffMins < 60) return `${diffMins}m`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h`;
  return `${Math.floor(diffHours / 24)}d`;
}
