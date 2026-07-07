"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark";

/** Reads/writes the [data-theme] attribute + persists to localStorage (key: pk-theme). */
export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const current = (document.documentElement.getAttribute("data-theme") as Theme) ?? "light";
    setTheme(current);
  }, []);

  const toggle = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem("pk-theme", next);
    } catch {
      /* private mode — ignore */
    }
    setTheme(next);
  };

  return (
    <button
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      className="cursor-pointer text-[13px] font-semibold"
      style={{
        border: "1px solid var(--pk-border)",
        background: "var(--pk-surface)",
        color: "var(--pk-text-2)",
        borderRadius: 999,
        padding: "7px 14px",
      }}
    >
      {theme === "dark" ? "☾ Dark" : "☀ Light"}
    </button>
  );
}
