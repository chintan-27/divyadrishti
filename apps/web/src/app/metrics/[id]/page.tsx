"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  fetchMetricDetail,
  fetchMetricSeries,
  type MetricDetail,
  type SeriesPoint,
} from "@/lib/api";
import ValenceBar from "@/components/ValenceBar";
import TimeSeriesChart from "@/components/TimeSeriesChart";
import StoryCard from "@/components/StoryCard";

const SERIES_FIELDS = [
  { key: "presence_pct", label: "Presence %", color: "#6366f1" },
  { key: "valence", label: "Valence", color: "#22c55e" },
  { key: "heat", label: "Heat", color: "#ef4444" },
  { key: "momentum", label: "Momentum", color: "#f59e0b" },
] as const;

export default function MetricDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<MetricDetail | null>(null);
  const [series, setSeries] = useState<SeriesPoint[]>([]);
  const [activeField, setActiveField] = useState<string>("presence_pct");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;

    Promise.all([
      fetchMetricDetail(params.id),
      fetchMetricSeries(params.id),
    ])
      .then(([d, s]) => {
        setDetail(d);
        setSeries(s);
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

  if (error || !detail) {
    return (
      <div className="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-400">
        {error ?? "Metric not found."}
      </div>
    );
  }

  const { rollup } = detail;
  const fieldConfig = SERIES_FIELDS.find((f) => f.key === activeField) ?? SERIES_FIELDS[0];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">{detail.label}</h1>
        <p className="mt-1 text-sm text-gray-400">{detail.definition}</p>
      </div>

      {/* Rollup stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Presence" value={`${rollup.presence_pct.toFixed(1)}%`} />
        <StatCard label="Heat" value={rollup.heat.toFixed(0)} />
        <StatCard label="Momentum" value={rollup.momentum >= 0 ? `+${rollup.momentum.toFixed(1)}` : rollup.momentum.toFixed(1)} />
        <StatCard label="Unique Authors" value={String(rollup.unique_authors)} />
      </div>

      {/* Valence */}
      <div className="card">
        <h2 className="mb-3 text-sm font-medium text-gray-400">Valence</h2>
        <ValenceBar valence={rollup.valence} />
        <div className="mt-3 flex gap-4 text-xs text-gray-500">
          <span>Split: {rollup.split.toFixed(1)}</span>
          <span>Consensus: {rollup.consensus >= 0 ? "+" : ""}{rollup.consensus.toFixed(1)}</span>
          <span>Window: {rollup.window}</span>
        </div>
      </div>

      {/* Time Series */}
      <div className="card">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-medium text-gray-400">Time Series</h2>
          <div className="flex gap-1 rounded-lg bg-surface-overlay p-1">
            {SERIES_FIELDS.map((f) => (
              <button
                key={f.key}
                onClick={() => setActiveField(f.key)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                  activeField === f.key
                    ? "bg-accent text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
        <TimeSeriesChart
          data={series}
          field={fieldConfig.key}
          color={fieldConfig.color}
        />
      </div>

      {/* Example Items */}
      {detail.example_items.length > 0 && (
        <div>
          <h2 className="mb-4 text-lg font-semibold">Example Items</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {detail.example_items.map((story) => (
              <StoryCard key={story.id} story={story} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="card text-center">
      <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold text-gray-100">{value}</p>
    </div>
  );
}
