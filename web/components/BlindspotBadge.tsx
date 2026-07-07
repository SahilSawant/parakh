/** High-contrast neutral badge — never a pole color (neutrality rule). */
export function BlindspotBadge({ compact = false }: { compact?: boolean }) {
  const px = compact ? 11 : 12;
  return (
    <span
      className="inline-flex w-fit items-center gap-1.5 font-semibold"
      style={{
        background: "var(--pk-blindspot-bg)",
        color: "var(--pk-blindspot-fg)",
        borderRadius: 5,
        padding: "4px 9px",
        fontSize: 10,
      }}
    >
      <svg width={px} height={px} viewBox="0 0 14 14" aria-hidden>
        <circle cx="7" cy="7" r="5.5" fill="none" stroke="currentColor" strokeWidth="1.6" />
        <rect x="1" y="6.2" width="12" height="1.6" fill="currentColor" transform="rotate(-45 7 7)" />
      </svg>
      Blindspot
    </span>
  );
}
