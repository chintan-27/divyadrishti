"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface TimeSeriesChartProps {
  data: Record<string, unknown>[];
  field: string;
  color?: string;
  height?: number;
}

export default function TimeSeriesChart({
  data,
  field,
  color = "#6366f1",
  height = 300,
}: TimeSeriesChartProps) {
  if (data.length === 0) {
    return (
      <div
        className="flex items-center justify-center text-sm text-gray-500"
        style={{ height }}
      >
        No time-series data available.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
        <XAxis
          dataKey="ts"
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickLine={false}
          axisLine={{ stroke: "#2a2d3e" }}
        />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          width={48}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1d2e",
            border: "1px solid #374151",
            borderRadius: "0.5rem",
            color: "#e5e7eb",
            fontSize: "0.8rem",
          }}
        />
        <Line
          type="monotone"
          dataKey={field}
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: color }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
