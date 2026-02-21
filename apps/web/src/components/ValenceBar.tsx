"use client";

interface ValenceBarProps {
  valence: number; // -100 to +100
  showValue?: boolean;
}

export default function ValenceBar({ valence, showValue = true }: ValenceBarProps) {
  const pct = (valence + 100) / 2;

  const barColor =
    valence > 15
      ? "bg-sentiment-positive"
      : valence < -15
        ? "bg-sentiment-negative"
        : "bg-sentiment-neutral";

  const textColor =
    valence > 15
      ? "text-green-400"
      : valence < -15
        ? "text-red-400"
        : "text-slate-400";

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2">
        <span className="w-8 text-right text-xs text-gray-600">−100</span>
        <div className="relative h-1.5 flex-1 rounded-full bg-surface-overlay">
          {/* Center tick */}
          <div className="absolute left-1/2 top-0 h-full w-px -translate-x-px bg-gray-700" />
          {/* Fill from center to value */}
          {valence >= 0 ? (
            <div
              className={`absolute top-0 left-1/2 h-full rounded-r-full ${barColor} opacity-60`}
              style={{ width: `${(valence / 100) * 50}%` }}
            />
          ) : (
            <div
              className={`absolute top-0 h-full rounded-l-full ${barColor} opacity-60`}
              style={{
                left: `${50 + (valence / 100) * 50}%`,
                width: `${(Math.abs(valence) / 100) * 50}%`,
              }}
            />
          )}
          {/* Dot indicator */}
          <div
            className={`absolute top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full border-2 border-surface-raised ${barColor}`}
            style={{ left: `calc(${pct}% - 5px)` }}
          />
        </div>
        <span className="w-8 text-xs text-gray-600">+100</span>
        {showValue && (
          <span className={`w-10 text-right text-xs font-semibold tabular-nums ${textColor}`}>
            {valence >= 0 ? "+" : ""}
            {valence.toFixed(0)}
          </span>
        )}
      </div>
    </div>
  );
}
