import { FACTUALITY, FactualityLevel } from "@/lib/buckets";

interface Props {
  level: FactualityLevel;
  size?: number;
}

/** The one traffic-light scale. Tooltip carries the label; color never stands alone. */
export function FactualityDot({ level, size = 10 }: Props) {
  const f = FACTUALITY[level];
  return (
    <span
      title={`Factuality: ${f.label}`}
      aria-label={`Factuality: ${f.label}`}
      role="img"
      className="inline-block shrink-0"
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: `var(${f.cssVar})`,
      }}
    />
  );
}
