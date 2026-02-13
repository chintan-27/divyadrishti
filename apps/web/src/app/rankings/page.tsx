"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchRankings,
  type Lens,
  type TimeWindow,
  type RankingEntry,
} from "@/lib/api";
import MetricCard from "@/components/MetricCard";
import LensTabs from "@/components/LensTabs";

const LENSES: { value: Lens; label: string }[] = [
  { value: "top", label: "Top" },
  { value: "controversial", label: "Controversial" },
  { value: "consensus_pos", label: "Consensus+" },
  { value: "consensus_neg", label: "Consensus-" },
  { value: "heated", label: "Heated" },
  { value: "rising", label: "Rising" },
];

const WINDOWS: { value: TimeWindow; label: string }[] = [
  { value: "hour", label: "Hour" },
  { value: "today", label: "Today" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
];

export default function RankingsPage() {
  const [lens, setLens] = useState<Lens>("top");
  const [window, setWindow] = useState<TimeWindow>("today");
  const [entries, setEntries] = useState<RankingEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRankings = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchRankings(window, lens)
      .then(setEntries)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [window, lens]);

  useEffect(() => {
    loadRankings();
  }, [loadRankings]);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Rankings</h1>

      {/* Controls */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <LensTabs lenses={LENSES} active={lens} onChange={setLens} />
        <LensTabs lenses={WINDOWS} active={window} onChange={setWindow} />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-400">
          Failed to load rankings: {error}
        </div>
      ) : entries.length === 0 ? (
        <p className="py-12 text-center text-gray-500">
          No rankings available for this lens and window.
        </p>
      ) : (
        <div className="space-y-3">
          {entries.map((entry) => (
            <div key={entry.metric.id} className="flex items-start gap-4">
              <span className="mt-5 w-8 shrink-0 text-right text-lg font-bold text-gray-600">
                {entry.rank}
              </span>
              <div className="flex-1">
                <MetricCard metric={entry.metric} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
