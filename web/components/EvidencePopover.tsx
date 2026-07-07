"use client";

import { useState, useRef, useEffect } from "react";

export interface EvidenceRow {
  stat: string; // "52", "3/3", "0.81", "→"
  text: string;
}

interface Props {
  rows: EvidenceRow[];
  lastUpdated: string;
  disputeHref: string;
  /** The trigger — usually a rating chip. Wrapped by the ⓘ affordance. */
  children: React.ReactNode;
}

/**
 * Trust surface: "Why this rating?" popover attached to a rating chip via an ⓘ
 * affordance. The dispute link is ALWAYS visible — never buried.
 */
export function EvidencePopover({ rows, lastUpdated, disputeHref, children }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onEsc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onEsc);
    };
  }, [open]);

  return (
    <span ref={ref as React.RefObject<HTMLSpanElement>} style={{ position: "relative", display: "inline-flex", alignItems: "center", gap: 4 }}>
      {children}
      <button
        aria-label="Why this rating?"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="cursor-pointer border-none bg-transparent"
        style={{ color: "var(--pk-text-3)", fontSize: 13, lineHeight: 1, padding: 2 }}
      >
        ⓘ
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Why this rating?"
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            left: 0,
            zIndex: 50,
            width: 320,
            background: "var(--pk-surface)",
            border: "1px solid var(--pk-border-strong)",
            borderRadius: "var(--pk-r-md)",
            padding: 18,
            boxShadow: "var(--pk-shadow-pop)",
          }}
          className="flex flex-col gap-3"
        >
          <div className="text-[13px] font-semibold" style={{ color: "var(--pk-text)" }}>
            Why this rating?
          </div>
          <div className="flex flex-col gap-2">
            {rows.map((r, i) => (
              <div key={i} className="flex items-baseline gap-[9px]">
                <span
                  style={{
                    fontFamily: "var(--pk-font-mono)",
                    fontSize: 12,
                    fontWeight: 500,
                    color: "var(--pk-brand)",
                    minWidth: 30,
                    textAlign: "right",
                  }}
                >
                  {r.stat}
                </span>
                <span className="text-[12px]" style={{ lineHeight: 1.45, color: "var(--pk-text-2)" }}>
                  {r.text}
                </span>
              </div>
            ))}
          </div>
          <div
            className="flex items-center justify-between"
            style={{ borderTop: "1px solid var(--pk-border)", paddingTop: 10 }}
          >
            <span className="text-[11px]" style={{ color: "var(--pk-text-3)" }}>
              Last updated {lastUpdated}
            </span>
            <a
              href={disputeHref}
              className="text-[12px] font-semibold"
              style={{ color: "var(--pk-brand)", textDecoration: "none" }}
            >
              Dispute this rating →
            </a>
          </div>
        </div>
      )}
    </span>
  );
}
