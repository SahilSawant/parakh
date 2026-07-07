import { ParallaxMark } from "@/components/ParallaxMark";

export interface OwnershipTier {
  tier: string; // "Outlet" | "Media group" | "Ultimate owner"
  name: string;
  note?: string;
}

interface Props {
  outletName: string; // for the "Who owns X?" header
  chain: OwnershipTier[];
  otherHoldings?: string;
  sourceNote?: string; // e.g. "sourced from exchange filings"
  permalink?: string; // e.g. "parakh.news/ndtv"
  onShareHref?: string;
}

const DOT_COLORS = ["var(--pk-brand)", "var(--pk-text-3)", "var(--pk-text)"];

/** Designed to screenshot — the organic growth unit. */
export function OwnershipCard({
  outletName,
  chain,
  otherHoldings,
  sourceNote = "sourced from exchange filings",
  permalink,
  onShareHref,
}: Props) {
  return (
    <div
      style={{
        background: "var(--pk-surface)",
        border: "1px solid var(--pk-border)",
        borderRadius: "var(--pk-r-lg)",
        padding: 22,
        boxShadow: "var(--pk-shadow-card)",
        maxWidth: 420,
      }}
    >
      <div
        className="flex items-center justify-between"
        style={{ paddingBottom: 14 }}
      >
        <span
          className="text-[12px] font-semibold uppercase"
          style={{ letterSpacing: "0.05em", color: "var(--pk-text-3)" }}
        >
          Who owns {outletName}?
        </span>
        <ParallaxMark size={20} />
      </div>

      {chain.map((o, i) => {
        const last = i === chain.length - 1;
        return (
          <div key={i} className="flex items-start gap-3">
            <div className="flex shrink-0 flex-col items-center">
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  border: `3px solid ${DOT_COLORS[Math.min(i, DOT_COLORS.length - 1)]}`,
                  background: "var(--pk-surface)",
                  boxSizing: "border-box",
                  marginTop: 4,
                }}
              />
              {!last && (
                <div style={{ width: 2, flex: 1, minHeight: 26, background: "var(--pk-border)" }} />
              )}
            </div>
            <div
              className="flex flex-col gap-0.5"
              style={{ paddingBottom: last ? 4 : 18 }}
            >
              <div
                className="text-[11px] font-medium uppercase"
                style={{ letterSpacing: "0.04em", color: "var(--pk-text-3)" }}
              >
                {o.tier}
              </div>
              <div className="text-[15px] font-semibold" style={{ color: "var(--pk-text)" }}>
                {o.name}
              </div>
              {o.note && (
                <div className="text-[12px]" style={{ color: "var(--pk-text-3)" }}>
                  {o.note}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {otherHoldings && (
        <div
          className="flex flex-col gap-1.5"
          style={{ borderTop: "1px solid var(--pk-border)", marginTop: 6, paddingTop: 12 }}
        >
          <div
            className="text-[11px] font-medium uppercase"
            style={{ letterSpacing: "0.04em", color: "var(--pk-text-3)" }}
          >
            Other media holdings
          </div>
          <div className="text-[13px]" style={{ color: "var(--pk-text-2)" }}>
            {otherHoldings}
          </div>
        </div>
      )}

      <div
        className="flex items-center justify-between"
        style={{ borderTop: "1px solid var(--pk-border)", marginTop: 12, paddingTop: 10 }}
      >
        <span className="text-[11px]" style={{ color: "var(--pk-text-3)" }}>
          {permalink ? `${permalink} · ` : ""}
          {sourceNote}
        </span>
        {onShareHref && (
          <a
            href={onShareHref}
            className="text-[12px] font-semibold"
            style={{ color: "var(--pk-brand)", textDecoration: "none" }}
          >
            Share ↗
          </a>
        )}
      </div>
    </div>
  );
}
