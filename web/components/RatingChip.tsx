import {
  Axis,
  GOVT_BUCKETS,
  IDEOLOGY_BUCKETS,
  GovtBucket,
  IdeologyBucket,
  tintBg,
  tintBorder,
  tintFg,
} from "@/lib/buckets";

type Size = "md" | "tiny";

interface RatingChipProps {
  axis: Axis;
  bucket: GovtBucket | IdeologyBucket | "pending";
  size?: Size;
  /** Optional shorter label for tiny chips in dense comparison rows. */
  short?: string;
}

function defFor(axis: Axis, bucket: string) {
  const list = axis === "govt" ? GOVT_BUCKETS : IDEOLOGY_BUCKETS;
  return list.find((b) => b.key === bucket);
}

/**
 * Pill per axis. The label text is always shown (never bare color) — survives
 * at every size and passes colorblindness. "Rating pending" is the neutral
 * gray state.
 */
export function RatingChip({ axis, bucket, size = "md", short }: RatingChipProps) {
  const tiny = size === "tiny";

  if (bucket === "pending") {
    return (
      <span
        className="inline-flex items-center font-semibold"
        style={{
          gap: tiny ? 4 : 6,
          borderRadius: 999,
          padding: tiny ? "2px 8px" : "5px 11px",
          fontSize: tiny ? 10 : 12,
          background: "var(--pk-surface-2)",
          color: "var(--pk-text-3)",
          border: "1px solid var(--pk-border)",
        }}
      >
        {!tiny && (
          <span
            className="shrink-0"
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "var(--pk-fact-pending)",
            }}
          />
        )}
        Rating pending
      </span>
    );
  }

  const def = defFor(axis, bucket);
  if (!def) return null;
  const label = short ?? def.label;

  return (
    <span
      className="inline-flex items-center font-semibold"
      style={{
        gap: tiny ? 4 : 6,
        borderRadius: 999,
        padding: tiny ? "2px 8px" : "5px 11px",
        fontSize: tiny ? 10 : 12,
        background: tintBg(def.cssVar),
        color: tintFg(def.cssVar),
        border: `1px solid ${tintBorder(def.cssVar)}`,
      }}
    >
      {!tiny && (
        <span
          className="shrink-0"
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: `var(${def.cssVar})`,
          }}
        />
      )}
      {label}
    </span>
  );
}
