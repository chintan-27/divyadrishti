"use client";

import { useEffect, useState } from "react";
import { fetchTrendingStories, type Story } from "@/lib/api";
import { useEventSource } from "@/lib/sse";
import StoryCard from "@/components/StoryCard";

export default function TrendingPage() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrendingStories()
      .then(setStories)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEventSource("/stream/trending", (event) => {
    try {
      const updated = JSON.parse(event.data) as Story;
      setStories((prev) => {
        const idx = prev.findIndex((s) => s.id === updated.id);
        if (idx >= 0) {
          const next = [...prev];
          next[idx] = updated;
          return next;
        }
        return [updated, ...prev];
      });
    } catch {
      // ignore malformed events
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-400">
        Failed to load stories: {error}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Trending Stories</h1>
        <span className="text-sm text-gray-500">
          {stories.length} stories
        </span>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stories.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))}
      </div>
      {stories.length === 0 && (
        <p className="py-12 text-center text-gray-500">
          No trending stories yet. Check back soon.
        </p>
      )}
    </div>
  );
}
