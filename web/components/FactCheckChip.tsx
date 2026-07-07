interface Props {
  /** The fact-checker, e.g. "Alt News", "BOOM". */
  checker: string;
  /** The verdict IN THE FACT-CHECKER'S OWN WORDS, quoted — never ours. */
  verdict: string;
  href?: string;
}

/**
 * Checkmark-shield = distinct visual class. Verdict wording is the
 * fact-checker's, quoted, never ours. Always links out.
 */
export function FactCheckChip({ checker, verdict, href }: Props) {
  const inner = (
    <>
      <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden>
        <path
          d="M7 1 L12 3 V7 C12 10 9.8 12.2 7 13 C4.2 12.2 2 10 2 7 V3 Z"
          fill="var(--pk-fact-very-high)"
        />
        <path
          d="M4.6 7.2 L6.3 8.9 L9.6 5.2"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
      <span>{checker}</span>{" "}
      <span style={{ fontWeight: 400, color: "var(--pk-text-2)" }}>{verdict}</span>
      {href && <span style={{ color: "var(--pk-brand)" }}> ↗</span>}
    </>
  );

  const style: React.CSSProperties = {
    border: "1.5px solid var(--pk-fact-very-high)",
    borderRadius: 8,
    padding: "7px 12px",
    fontSize: 12,
    fontWeight: 600,
    color: "color-mix(in srgb, var(--pk-fact-very-high) 78%, var(--pk-text))",
    background: "color-mix(in srgb, var(--pk-fact-very-high) 8%, var(--pk-surface))",
    textDecoration: "none",
  };

  const cls = "inline-flex items-center gap-[7px]";
  return href ? (
    <a href={href} target="_blank" rel="noopener noreferrer" className={cls} style={style}>
      {inner}
    </a>
  ) : (
    <span className={cls} style={style}>
      {inner}
    </span>
  );
}
