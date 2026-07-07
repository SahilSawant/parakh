/**
 * Bucket definitions — the single source of truth for the two bias axes and
 * factuality, bound to the design tokens (never a raw hex). Colors are CSS
 * variable references so light/dark theming resolves at runtime.
 *
 * Design rules encoded here:
 *  - Equal, non-warning poles on both axes (neutrality audit, §3).
 *  - The two "lean" segments carry a diagonal hatch (colorblind rule).
 *  - Labels are plain words, identical in connotation across poles.
 *  - हिंदी is always Devanagari, never the word "Hindi".
 */

export type Axis = "govt" | "ideology";

export type GovtBucket =
  | "pro"
  | "lean_pro"
  | "mixed"
  | "lean_critical"
  | "critical";

export type IdeologyBucket =
  | "left"
  | "lean_left"
  | "centre"
  | "lean_right"
  | "right";

export type FactualityLevel =
  | "very_high"
  | "high"
  | "mixed"
  | "low"
  | "very_low"
  | "pending";

export interface BucketDef<K extends string> {
  key: K;
  label: string;
  /** CSS variable reference for the solid segment/dot color. */
  cssVar: string;
  /** "lean" buckets get the diagonal hatch so five buckets survive colorblindness. */
  hatch: boolean;
}

export const GOVT_BUCKETS: BucketDef<GovtBucket>[] = [
  { key: "pro", label: "Pro-establishment", cssVar: "--pk-govt-pro", hatch: false },
  { key: "lean_pro", label: "Lean pro", cssVar: "--pk-govt-lean-pro", hatch: true },
  { key: "mixed", label: "Mixed", cssVar: "--pk-govt-mixed", hatch: false },
  { key: "lean_critical", label: "Lean critical", cssVar: "--pk-govt-lean-crit", hatch: true },
  { key: "critical", label: "Critical", cssVar: "--pk-govt-crit", hatch: false },
];

export const IDEOLOGY_BUCKETS: BucketDef<IdeologyBucket>[] = [
  { key: "left", label: "Left", cssVar: "--pk-ideo-left", hatch: false },
  { key: "lean_left", label: "Lean left", cssVar: "--pk-ideo-lean-left", hatch: true },
  { key: "centre", label: "Centre", cssVar: "--pk-ideo-center", hatch: false },
  { key: "lean_right", label: "Lean right", cssVar: "--pk-ideo-lean-right", hatch: true },
  { key: "right", label: "Right", cssVar: "--pk-ideo-right", hatch: false },
];

export const FACTUALITY: Record<FactualityLevel, { label: string; cssVar: string }> = {
  very_high: { label: "Very high", cssVar: "--pk-fact-very-high" },
  high: { label: "High", cssVar: "--pk-fact-high" },
  mixed: { label: "Mixed", cssVar: "--pk-fact-mixed" },
  low: { label: "Low", cssVar: "--pk-fact-low" },
  very_low: { label: "Very low", cssVar: "--pk-fact-very-low" },
  pending: { label: "Rating pending", cssVar: "--pk-fact-pending" },
};

export const AXIS_LABEL: Record<Axis, string> = {
  govt: "Govt alignment",
  ideology: "Ideology",
};

export function bucketsFor(axis: Axis): BucketDef<string>[] {
  return axis === "govt" ? GOVT_BUCKETS : IDEOLOGY_BUCKETS;
}

/** The design's bias-bar gate: a distribution renders only at >= 5 rated outlets. */
export const MIN_RATED_FOR_DISTRIBUTION = 5;

export function cssVar(name: string): string {
  return `var(${name})`;
}

/**
 * Theme-adaptive tint derived from a bucket token via color-mix — keeps chips
 * token-driven (no hardcoded tint hexes) and correct in both light and dark.
 */
export function tintBg(varName: string): string {
  return `color-mix(in srgb, var(${varName}) 14%, var(--pk-surface))`;
}
export function tintBorder(varName: string): string {
  return `color-mix(in srgb, var(${varName}) 34%, var(--pk-surface))`;
}
export function tintFg(varName: string): string {
  // Mix toward the page ink so contrast holds whichever theme is active.
  return `color-mix(in srgb, var(${varName}) 62%, var(--pk-text))`;
}
