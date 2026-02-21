"use client";

import Link from "next/link";
import type { MetricNode } from "@/lib/api";

interface MetricCardProps {
  metric: MetricNode;
  index?: number;
}

export default function MetricCard({ metric, index = 0 }: MetricCardProps) {
  const heatLevel =
    metric.heat >= 80
      ? { label: "Hot", textColor: "text-red-400", dot: "bg-red-500" }
      : metric.heat >= 40
        ? { label: "Warm", textColor: "text-amber-400", dot: "bg-amber-500" }
        : { label: "Cool", textColor: "text-blue-400", dot: "bg-blue-400" };

  const momentumSign = metric.momentum >= 0 ? "+" : "";
  const momentumColor =
    metric.momentum > 2
      ? "text-green-400"
      : metric.momentum < -2
        ? "text-red-400"
        : "text-gray-500";
  const momentumArrow = metric.momentum > 2 ? "↑" : metric.momentum < -2 ? "↓" : "→";

  const valenceColor =
    metric.valence > 15
      ? "text-green-400"
      : metric.valence < -15
        ? "text-red-400"
        : "text-slate-400";

  const total =
    metric.sentiment.positive + metric.sentiment.negative + metric.sentiment.neutral;
  const posPct = total > 0 ? (metric.sentiment.positive / total) * 100 : 0;
  const negPct = total > 0 ? (metric.sentiment.negative / total) * 100 : 0;
  const neuPct = total > 0 ? (metric.sentiment.neutral / total) * 100 : 0;

  return (
    <Link
      href={`/metrics/${metric.id}`}
      className="card card-animate block group"
      style={{ animationDelay: `${index * 40}ms` }}
    >
      {/* Top row: heat + momentum */}
      <div className="mb-3 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs font-medium">
          <span className={`h-1.5 w-1.5 rounded-full ${heatLevel.dot}`} />
          <span className={heatLevel.textColor}>{heatLevel.label}</span>
        </span>
        <span className={`text-xs font-semibold tabular-nums ${momentumColor}`}>
          {momentumArrow} {momentumSign}{metric.momentum.toFixed(1)}
        </span>
      </div>

      {/* Label */}
      <h2 className="mb-4 font-semibold leading-snug text-gray-100 line-clamp-2 group-hover:text-white transition-colors">
        {metric.label}
      </h2>

      {/* Presence + Valence */}
      <div className="mb-4 flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold tabular-nums text-white leading-none">
            {metric.presence_pct.toFixed(1)}
            <span className="text-sm font-medium text-gray-500 ml-0.5">%</span>
          </p>
          <p className="mt-0.5 text-xs text-gray-500 uppercase tracking-wide">presence</p>
        </div>
        <div className="text-right">
          <p className={`text-2xl font-bold tabular-nums leading-none ${valenceColor}`}>
            {metric.valence >= 0 ? "+" : ""}
            {metric.valence.toFixed(0)}
          </p>
          <p className="mt-0.5 text-xs text-gray-500 uppercase tracking-wide">valence</p>
        </div>
      </div>

      {/* Sentiment bar */}
      {total > 0 ? (
        <div>
          <div className="flex h-1 w-full overflow-hidden rounded-full gap-px">
            <div
              className="bg-sentiment-positive rounded-l-full"
              style={{ width: `${posPct}%` }}
            />
            <div className="bg-sentiment-neutral" style={{ width: `${neuPct}%` }} />
            <div
              className="bg-sentiment-negative rounded-r-full"
              style={{ width: `${negPct}%` }}
            />
          </div>
          <div className="mt-1.5 flex gap-3 text-xs">
            <span className="text-green-500">{posPct.toFixed(0)}% pos</span>
            <span className="text-gray-500">{neuPct.toFixed(0)}% neu</span>
            <span className="text-red-500">{negPct.toFixed(0)}% neg</span>
          </div>
        </div>
      ) : (
        <div className="h-1 w-full rounded-full bg-gray-800" />
      )}
    </Link>
  );
}
