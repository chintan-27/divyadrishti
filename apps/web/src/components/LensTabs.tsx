"use client";

interface LensTabsProps<T extends string> {
  lenses: { value: T; label: string }[];
  active: T;
  onChange: (lens: T) => void;
}

export default function LensTabs<T extends string>({
  lenses,
  active,
  onChange,
}: LensTabsProps<T>) {
  return (
    <div className="flex flex-wrap gap-1 rounded-lg bg-surface-overlay p-1">
      {lenses.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onChange(value)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            active === value
              ? "bg-accent text-white shadow-sm"
              : "text-gray-400 hover:text-white hover:bg-surface-raised"
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
