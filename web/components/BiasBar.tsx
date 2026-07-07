"use client";

import { useState } from "react";
import {
  Axis,
  AXIS_LABEL,
  bucketsFor,
  MIN_RATED_FOR_DISTRIBUTION,
} from "@/lib/buckets";

export type Distribution = Record<string, number>; // bucketKey -> percent (0..100)

interface BiasBarProps {
  /** Percent per govt bucket key (pro, lean_pro, mixed, lean_critical, critical). */
  distGovt: Distribution;
  /** Percent per ideology bucket key. Enables the axis toggle when present. */
  distIdeology?: Distribution;
  ratedCount: number;
  variant?: "full" | "mini";
  defaultAxis?: Axis;
  outletsLabel?: string;
  className?: string;
}

function Segments({ axis, dist }: { axis: Axis; dist: Distribution }) {
  return (
    <div
      className="flex h-6 gap-[2px] overflow-hidden"
      style={{ borderRadius: "var(--pk-r-sm)" }}
      role="img"
      aria-label={bucketsFor(axis)
        .filter((b) => (dist[b.key] ?? 0) > 0)
        .map((b) => `${b.label} ${Math.round(dist[b.key])}%`)
        .join(", ")}
    >
      {bucketsFor(axis).map((b) => {
        const w = dist[b.key] ?? 0;
        if (w <= 0) return null;
        return (
          <div
            key={b.key}
            title={`${b.label} ${Math.round(w)}%`}
            className={b.hatch ? "relative pk-hatch" : "relative"}
            style={{ width: `${w}%`, background: `var(${b.cssVar})` }}
          />
        );
      })}
    </div>
  );
}

function Legend({ axis, dist }: { axis: Axis; dist: Distribution }) {
  return (
    <div className="flex flex-wrap justify-between gap-2">
      {bucketsFor(axis)
        .filter((b) => (dist[b.key] ?? 0) > 0)
        .map((b) => (
          <span
            key={b.key}
            className="inline-flex items-center gap-1.5 text-[12px]"
            style={{ color: "var(--pk-text-2)" }}
          >
            <span
              className="h-[9px] w-[9px] shrink-0"
              style={{ background: `var(${b.cssVar})`, borderRadius: "2px" }}
            />
            <strong style={{ fontWeight: 600, color: "var(--pk-text)" }}>
              {Math.round(dist[b.key])}%
            </strong>{" "}
            {b.label}
          </span>
        ))}
    </div>
  );
}

/** Insufficient / empty state — hatched placeholder + honest copy. */
function Insufficient({ ratedCount, mini }: { ratedCount: number; mini?: boolean }) {
  return (
    <div className="flex flex-col gap-[7px]">
      <div
        aria-hidden
        style={{
          height: mini ? 8 : 12,
          width: 80,
          borderRadius: 3,
          background:
            "repeating-linear-gradient(-45deg, var(--pk-border) 0 4px, var(--pk-surface-2) 4px 8px)",
        }}
      />
      <div className="text-[11px]" style={{ color: "var(--pk-text-3)" }}>
        {ratedCount} {ratedCount === 1 ? "source" : "sources"} — not enough for a
        distribution
      </div>
    </div>
  );
}

export function BiasBar({
  distGovt,
  distIdeology,
  ratedCount,
  variant = "full",
  defaultAxis = "govt",
  outletsLabel,
  className,
}: BiasBarProps) {
  const [axis, setAxis] = useState<Axis>(defaultAxis);
  const canToggle = variant === "full" && !!distIdeology;
  const dist = axis === "ideology" && distIdeology ? distIdeology : distGovt;
  const insufficient = ratedCount < MIN_RATED_FOR_DISTRIBUTION;

  // ---- Mini (story card) ----
  if (variant === "mini") {
    if (insufficient) {
      return (
        <div className={className}>
          <Insufficient ratedCount={ratedCount} mini />
        </div>
      );
    }
    const govt = bucketsFor("govt");
    return (
      <div className={`flex items-center gap-2.5 ${className ?? ""}`}>
        <div
          className="flex h-2 w-20 shrink-0 gap-px overflow-hidden"
          style={{ borderRadius: 3 }}
          role="img"
          aria-label="Government-alignment coverage distribution"
        >
          {govt.map((b) => {
            const w = distGovt[b.key] ?? 0;
            if (w <= 0) return null;
            return (
              <div
                key={b.key}
                style={{ width: `${w}%`, background: `var(${b.cssVar})` }}
              />
            );
          })}
        </div>
      </div>
    );
  }

  // ---- Full (story page) ----
  return (
    <div
      className={`flex flex-col gap-3 ${className ?? ""}`}
      style={{
        background: "var(--pk-surface)",
        border: "1px solid var(--pk-border)",
        borderRadius: "var(--pk-r-md)",
        padding: "20px 22px",
      }}
    >
      <div className="flex items-center justify-between">
        {canToggle ? (
          <div
            role="tablist"
            aria-label="Bias axis"
            className="flex gap-0.5 p-[3px]"
            style={{ background: "var(--pk-surface-2)", borderRadius: 999 }}
          >
            {(["govt", "ideology"] as Axis[]).map((a) => {
              const active = axis === a;
              return (
                <button
                  key={a}
                  role="tab"
                  aria-selected={active}
                  onClick={() => setAxis(a)}
                  className="cursor-pointer border-none text-[12px] font-semibold"
                  style={{
                    borderRadius: 999,
                    padding: "6px 14px",
                    background: active ? "var(--pk-surface)" : "transparent",
                    color: active ? "var(--pk-text)" : "var(--pk-text-3)",
                    boxShadow: active ? "var(--pk-shadow-card)" : "none",
                  }}
                >
                  {AXIS_LABEL[a]}
                </button>
              );
            })}
          </div>
        ) : (
          <span className="text-[12px] font-semibold" style={{ color: "var(--pk-text-2)" }}>
            {AXIS_LABEL[axis]}
          </span>
        )}
        {outletsLabel && (
          <span className="text-[12px]" style={{ color: "var(--pk-text-3)" }}>
            {outletsLabel}
          </span>
        )}
      </div>

      {insufficient ? (
        <Insufficient ratedCount={ratedCount} />
      ) : (
        <>
          <Segments axis={axis} dist={dist} />
          <Legend axis={axis} dist={dist} />
        </>
      )}
    </div>
  );
}
