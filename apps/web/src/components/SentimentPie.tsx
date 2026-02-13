"use client";

import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";

interface SentimentPieProps {
  positive: number;
  negative: number;
  neutral: number;
}

const COLORS = {
  Positive: "#22c55e",
  Negative: "#ef4444",
  Neutral: "#94a3b8",
};

export default function SentimentPie({
  positive,
  negative,
  neutral,
}: SentimentPieProps) {
  const total = positive + negative + neutral;

  if (total === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-500">
        No sentiment data available
      </p>
    );
  }

  const data = [
    { name: "Positive", value: positive },
    { name: "Negative", value: negative },
    { name: "Neutral", value: neutral },
  ].filter((d) => d.value > 0);

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={90}
          paddingAngle={3}
          dataKey="value"
          stroke="none"
        >
          {data.map((entry) => (
            <Cell
              key={entry.name}
              fill={COLORS[entry.name as keyof typeof COLORS]}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1d2e",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#e5e7eb",
          }}
          formatter={(value: number) => {
            const pct = ((value / total) * 100).toFixed(1);
            return [`${value} (${pct}%)`, ""];
          }}
        />
        <Legend
          verticalAlign="bottom"
          iconType="circle"
          formatter={(value: string) => (
            <span className="text-sm text-gray-300">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
