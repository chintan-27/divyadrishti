"use client";

import Link from "next/link";
import type { MetricNode } from "@/lib/api";
import ValenceBar from "@/components/ValenceBar";

interface MetricCardProps {
  metric: MetricNode;
}

export default function MetricCard({ metric }: MetricCardProps) {
  const heatLevel =
    metric.heat >= 80
      ? { label: "Hot", color: "bg-red-500/20 text-red-400" }
      : metric.heat >= 40
        ? { label: "Warm", color: "bg-amber-500/20 text-amber-400" }
        : { label: "Cool", color: "bg-blue-500/20 text-blue-400" };

  return (
    <Link href={`/metrics/${metric.id}`} className="card block">
      <div className="mb-3 flex items-start justify-between gap-2">
        <h2 className="font-semibold leading-snug text-gray-100 line-clamp-2">
          {metric.label}
        </h2>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${heatLevel.color}`}
        >
          {heatLevel.label}
        </span>
      </div>
      <div className="mb-3 flex items-baseline gap-3 text-sm">
        <span className="font-medium text-accent">
          {metric.presence_pct.toFixed(1)}%
        </span>
        <span className="text-xs text-gray-500">presence</span>
        <span className="ml-auto text-xs text-gray-500">
          heat {metric.heat.toFixed(0)}
        </span>
      </div>
      <ValenceBar valence={metric.valence} />
    </Link>
  );
}
