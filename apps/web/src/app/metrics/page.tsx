"use client";

import { useEffect, useState } from "react";
import { fetchTopMetrics, type MetricNode } from "@/lib/api";
import MetricCard from "@/components/MetricCard";

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<MetricNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTopMetrics()
      .then(setMetrics)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

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
        Failed to load metrics: {error}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Top Metrics</h1>
        <span className="text-sm text-gray-500">
          {metrics.length} metric nodes
        </span>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <MetricCard key={metric.id} metric={metric} />
        ))}
      </div>
      {metrics.length === 0 && (
        <p className="py-12 text-center text-gray-500">
          No metric nodes discovered yet. Check back once ingestion is running.
        </p>
      )}
    </div>
  );
}
