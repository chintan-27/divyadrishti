"use client";

interface ValenceBarProps {
  valence: number; // -100 to +100
}

export default function ValenceBar({ valence }: ValenceBarProps) {
  // Normalize valence to 0-100 range for positioning (0 = -100, 50 = 0, 100 = +100)
  const pct = (valence + 100) / 2;

  const barColor =
    valence > 15
      ? "bg-sentiment-positive"
      : valence < -15
        ? "bg-sentiment-negative"
        : "bg-sentiment-neutral";

  return (
    <div className="flex items-center gap-2">
      <span className="w-8 text-right text-xs text-gray-500">-100</span>
      <div className="relative h-2 flex-1 rounded-full bg-surface-overlay">
        {/* Center tick */}
        <div className="absolute left-1/2 top-0 h-full w-px -translate-x-px bg-gray-600" />
        {/* Value indicator */}
        <div
          className={`absolute top-0 h-full w-2 rounded-full ${barColor}`}
          style={{ left: `calc(${pct}% - 4px)` }}
        />
        {/* Fill from center to value */}
        {valence >= 0 ? (
          <div
            className={`absolute top-0 left-1/2 h-full rounded-r-full ${barColor} opacity-40`}
            style={{ width: `${(valence / 100) * 50}%` }}
          />
        ) : (
          <div
            className={`absolute top-0 h-full rounded-l-full ${barColor} opacity-40`}
            style={{
              left: `${50 + (valence / 100) * 50}%`,
              width: `${(Math.abs(valence) / 100) * 50}%`,
            }}
          />
        )}
      </div>
      <span className="w-8 text-xs text-gray-500">+100</span>
    </div>
  );
}
