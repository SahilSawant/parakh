"use client";

import { useState } from "react";

export type ContentLang = "all" | "en" | "hi";

const OPTIONS: { key: ContentLang; label: string; dev?: boolean }[] = [
  { key: "all", label: "All" },
  { key: "en", label: "English" },
  { key: "hi", label: "हिंदी", dev: true }, // always Devanagari, never "Hindi"
];

/** Content-language filter, persistent in the top bar. */
export function LanguageToggle({
  value,
  onChange,
}: {
  value?: ContentLang;
  onChange?: (v: ContentLang) => void;
}) {
  const [internal, setInternal] = useState<ContentLang>(value ?? "all");
  const active = value ?? internal;
  const set = (v: ContentLang) => {
    setInternal(v);
    onChange?.(v);
  };

  return (
    <div
      role="radiogroup"
      aria-label="Content language"
      className="flex w-fit gap-0.5 p-[3px]"
      style={{ background: "var(--pk-surface-2)", borderRadius: 999 }}
    >
      {OPTIONS.map((o) => {
        const on = active === o.key;
        return (
          <button
            key={o.key}
            role="radio"
            aria-checked={on}
            onClick={() => set(o.key)}
            className="cursor-pointer border-none text-[13px] font-semibold"
            lang={o.dev ? "hi" : undefined}
            style={{
              borderRadius: 999,
              padding: "7px 16px",
              fontFamily: o.dev ? "var(--pk-font-dev)" : "var(--pk-font-ui)",
              background: on ? "var(--pk-surface)" : "transparent",
              color: on ? "var(--pk-text)" : "var(--pk-text-3)",
              boxShadow: on ? "var(--pk-shadow-card)" : "none",
            }}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
