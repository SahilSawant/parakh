import { BiasBar, Distribution } from "@/components/BiasBar";
import { BlindspotBadge } from "@/components/BlindspotBadge";

export interface StoryCardData {
  title: string;
  lang?: "en" | "hi";
  outletCount: number;
  timeAgo: string;
  distGovt: Distribution;
  ratedCount: number;
  blindspot?: boolean;
  aiSummarized?: boolean;
  href?: string;
  /** Optional image URL; when absent a neutral placeholder renders (data-saver / no image). */
  imageUrl?: string;
}

function summaryLine(dist: Distribution): string {
  const pro = Math.round((dist.pro ?? 0) + (dist.lean_pro ?? 0));
  const crit = Math.round((dist.critical ?? 0) + (dist.lean_critical ?? 0));
  return `${pro}% pro-est · ${crit}% critical`;
}

const AiMark = ({ dark = false }: { dark?: boolean }) => (
  <span
    className="inline-flex items-center gap-1"
    style={{
      background: dark ? "var(--pk-surface-2)" : "var(--pk-surface-2)",
      borderRadius: 4,
      padding: "2px 7px",
      fontWeight: 500,
    }}
  >
    ✦ AI-summarized
  </span>
);

export function StoryCard({
  data,
  variant = "full",
}: {
  data: StoryCardData;
  variant?: "full" | "compact";
}) {
  const hi = data.lang === "hi";
  const titleStyle: React.CSSProperties = hi
    ? { fontFamily: "var(--pk-font-dev)", lineHeight: 1.6 }
    : { lineHeight: 1.45 };

  const Wrapper = ({ children }: { children: React.ReactNode }) =>
    data.href ? (
      <a href={data.href} style={{ textDecoration: "none", color: "inherit" }}>
        {children}
      </a>
    ) : (
      <>{children}</>
    );

  if (variant === "compact") {
    return (
      <Wrapper>
        <div
          className="flex gap-3"
          style={{ padding: "12px 14px", borderTop: "1px solid var(--pk-border)" }}
        >
          <div
            className="shrink-0"
            style={{
              width: 64,
              height: 64,
              borderRadius: 8,
              background: data.imageUrl
                ? `center/cover no-repeat url(${data.imageUrl})`
                : "repeating-linear-gradient(-45deg, var(--pk-surface-2) 0 8px, var(--pk-border) 8px 16px)",
            }}
          />
          <div className="flex min-w-0 flex-col gap-1.5">
            <div
              className="text-[14px] font-medium"
              lang={hi ? "hi" : undefined}
              style={{ ...titleStyle, color: "var(--pk-text)" }}
            >
              {data.title}
            </div>
            <div className="flex items-center gap-2">
              <BiasBar
                variant="mini"
                distGovt={data.distGovt}
                ratedCount={data.ratedCount}
              />
              <span
                className="whitespace-nowrap text-[10px]"
                style={{ color: "var(--pk-text-3)" }}
              >
                {data.outletCount} outlets · {data.timeAgo}
              </span>
            </div>
          </div>
        </div>
      </Wrapper>
    );
  }

  // ---- Full card ----
  return (
    <Wrapper>
      <div
        style={{
          width: "100%",
          maxWidth: 340,
          background: "var(--pk-surface)",
          border: "1px solid var(--pk-border)",
          borderRadius: "var(--pk-r-md)",
          overflow: "hidden",
          boxShadow: "var(--pk-shadow-card)",
        }}
      >
        <div
          style={{
            position: "relative",
            height: 150,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: data.imageUrl
              ? `center/cover no-repeat url(${data.imageUrl})`
              : "repeating-linear-gradient(-45deg, var(--pk-surface-2) 0 10px, var(--pk-border) 10px 20px)",
          }}
        >
          {!data.imageUrl && (
            <span
              style={{
                fontFamily: "var(--pk-font-mono)",
                fontSize: 11,
                color: "var(--pk-text-3)",
              }}
            >
              story image
            </span>
          )}
          {data.blindspot && (
            <span style={{ position: "absolute", top: 10, left: 10 }}>
              <BlindspotBadge />
            </span>
          )}
        </div>
        <div className="flex flex-col gap-[9px]" style={{ padding: "14px 16px 16px" }}>
          <div
            className="text-[16px] font-medium"
            lang={hi ? "hi" : undefined}
            style={{ ...titleStyle, color: "var(--pk-text)" }}
          >
            {data.title}
          </div>
          <div
            className="flex items-center gap-2 text-[11px]"
            style={{ color: "var(--pk-text-3)" }}
          >
            {data.aiSummarized !== false && <AiMark />}
            <span>{data.outletCount} outlets</span>
            <span>·</span>
            <span>{data.timeAgo}</span>
          </div>
          <div className="flex items-center gap-2.5">
            <BiasBar
              variant="mini"
              distGovt={data.distGovt}
              ratedCount={data.ratedCount}
            />
            {data.ratedCount >= 5 && (
              <span className="text-[11px]" style={{ color: "var(--pk-text-2)" }}>
                {summaryLine(data.distGovt)}
              </span>
            )}
          </div>
        </div>
      </div>
    </Wrapper>
  );
}
