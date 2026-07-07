interface Props {
  size?: number;
  /** Monochrome favicon/monogram mode (uses currentColor). */
  mono?: boolean;
  title?: string;
}

/**
 * Parakh mark — two offset circles (teal + plum) forming one image: a parallax
 * of two viewpoints. Works at 24px and in monochrome (design: Naming & Logo).
 */
export function ParallaxMark({ size = 28, mono = false, title = "Parakh" }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 56 56"
      role="img"
      aria-label={title}
      fill="none"
    >
      <circle
        cx="23"
        cy="28"
        r="16"
        fill={mono ? "currentColor" : "var(--pk-govt-pro)"}
        opacity={mono ? 0.55 : 0.85}
      />
      <circle
        cx="33"
        cy="28"
        r="16"
        fill={mono ? "currentColor" : "var(--pk-govt-crit)"}
        opacity={mono ? 0.85 : 0.85}
      />
    </svg>
  );
}
