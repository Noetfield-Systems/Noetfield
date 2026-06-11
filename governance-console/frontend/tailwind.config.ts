import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      colors: {
        surface: "rgb(var(--bg0-rgb) / <alpha-value>)",
        panel: "rgb(var(--white-rgb) / <alpha-value>)",
        "panel-solid": "rgb(var(--bg1-rgb) / <alpha-value>)",
        border: "rgb(var(--white-rgb) / <alpha-value>)",
        muted: "rgb(var(--muted-rgb) / <alpha-value>)",
        "muted-2": "rgb(var(--muted2-rgb) / <alpha-value>)",
        accent: "rgb(var(--gold-rgb) / <alpha-value>)",
        "accent-dim": "var(--gold-dim)",
        ok: "rgb(var(--ok-rgb) / <alpha-value>)",
      },
      boxShadow: {
        panel: "var(--shadow)",
        glow: "0 0 40px rgba(200,163,73,0.12)",
      },
      borderRadius: {
        xl: "var(--radius)",
        lg: "var(--radius-sm)",
      },
    },
  },
  plugins: [],
};

export default config;
