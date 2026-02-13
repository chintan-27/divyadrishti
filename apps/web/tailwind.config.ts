import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        surface: {
          DEFAULT: "#0f1117",
          raised: "#1a1d2e",
          overlay: "#232738",
        },
        accent: {
          DEFAULT: "#6366f1",
          hover: "#818cf8",
        },
        sentiment: {
          positive: "#22c55e",
          negative: "#ef4444",
          neutral: "#94a3b8",
        },
      },
    },
  },
  plugins: [],
};

export default config;
