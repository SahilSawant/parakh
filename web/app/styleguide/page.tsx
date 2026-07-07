import type { Metadata } from "next";
import { BiasBar } from "@/components/BiasBar";
import { RatingChip } from "@/components/RatingChip";
import { FactualityDot } from "@/components/FactualityDot";
import { StoryCard, StoryCardData } from "@/components/StoryCard";
import { OwnershipCard } from "@/components/OwnershipCard";
import { FactCheckChip } from "@/components/FactCheckChip";
import { BlindspotBadge } from "@/components/BlindspotBadge";
import { LanguageToggle } from "@/components/LanguageToggle";
import { ThemeToggle } from "@/components/ThemeToggle";
import { EvidencePopover } from "@/components/EvidencePopover";
import { ParallaxMark } from "@/components/ParallaxMark";
import {
  GOVT_BUCKETS,
  IDEOLOGY_BUCKETS,
  FactualityLevel,
} from "@/lib/buckets";

export const metadata: Metadata = { title: "Component gallery" };

// ---- FICTIONAL demo data for design review — not editorial claims. ----
const DIST_GOVT = { pro: 38, lean_pro: 22, mixed: 28, lean_critical: 7, critical: 5 };
const DIST_IDEO = { left: 9, lean_left: 15, centre: 41, lean_right: 21, right: 14 };

const STORY_EN: StoryCardData = {
  title: "Centre notifies data protection rules; industry bodies seek six-month transition",
  outletCount: 34,
  timeAgo: "2h ago",
  distGovt: DIST_GOVT,
  ratedCount: 34,
};
const STORY_HI: StoryCardData = {
  title: "डेटा संरक्षण नियम अधिसूचित, उद्योग ने छह महीने का समय मांगा",
  lang: "hi",
  outletCount: 34,
  timeAgo: "2h ago",
  distGovt: DIST_GOVT,
  ratedCount: 34,
  blindspot: true,
};
const COMPACT: StoryCardData[] = [
  { title: "SEBI proposes tighter F&O disclosure norms for retail brokers", outletCount: 18, timeAgo: "4h", distGovt: { pro: 45, mixed: 40, critical: 15 }, ratedCount: 18 },
  { title: "रेलवे ने तीन नई वंदे भारत स्लीपर ट्रेनों की घोषणा की", lang: "hi", outletCount: 26, timeAgo: "1h", distGovt: { pro: 70, mixed: 25, critical: 5 }, ratedCount: 26 },
  { title: "Kerala HC stays local body delimitation order", outletCount: 9, timeAgo: "6h", distGovt: { pro: 20, mixed: 35, critical: 45 }, ratedCount: 9 },
];

const FACT_LEVELS: FactualityLevel[] = ["very_high", "high", "mixed", "low", "very_low", "pending"];

function Card({
  id,
  title,
  hint,
  children,
}: {
  id: string;
  title: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <section
      id={id}
      className="flex flex-col gap-4"
      style={{
        background: "var(--pk-surface)",
        border: "1px solid var(--pk-border)",
        borderRadius: "var(--pk-r-lg)",
        padding: 24,
      }}
    >
      <div className="flex items-baseline gap-3">
        <h2 className="text-[18px] font-semibold" style={{ color: "var(--pk-text)" }}>
          {title}
        </h2>
        {hint && (
          <span className="text-[12px]" style={{ color: "var(--pk-text-3)" }}>
            {hint}
          </span>
        )}
      </div>
      {children}
    </section>
  );
}

const Label = ({ children }: { children: React.ReactNode }) => (
  <div
    className="text-[10px] font-medium uppercase"
    style={{ letterSpacing: "0.05em", color: "var(--pk-text-3)" }}
  >
    {children}
  </div>
);

export default function Styleguide() {
  return (
    <main
      style={{ minHeight: "100dvh", background: "var(--pk-bg)" }}
      className="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-10"
    >
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <ParallaxMark size={28} />
          <div>
            <div className="text-[20px] font-semibold" style={{ color: "var(--pk-text)" }}>
              Parakh · Component gallery
            </div>
            <div className="text-[12px]" style={{ color: "var(--pk-text-3)" }}>
              §4 primitives — all states, light + dark
            </div>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <div
        className="text-[13px]"
        style={{
          background: "var(--pk-brand-tint)",
          color: "var(--pk-brand-strong)",
          border: "1px solid var(--pk-border)",
          borderRadius: "var(--pk-r-md)",
          padding: "10px 14px",
        }}
      >
        All ratings below are <strong>fictional demo data</strong> for design review — not
        editorial claims about any outlet. Toggle the theme to check dark-mode parity.
      </div>

      <Card id="bias-bar" title="Dual-axis bias bar" hint="full · mini · empty — toggle is live, hatch on lean">
        <BiasBar
          distGovt={DIST_GOVT}
          distIdeology={DIST_IDEO}
          ratedCount={34}
          outletsLabel="34 outlets"
        />
        <div className="flex flex-wrap items-start gap-6">
          <div className="flex flex-col gap-2">
            <Label>Mini · story card</Label>
            <div className="flex items-center gap-2.5">
              <BiasBar variant="mini" distGovt={DIST_GOVT} ratedCount={34} />
              <span className="text-[11px]" style={{ color: "var(--pk-text-2)" }}>
                60% pro-est · 12% critical
              </span>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <Label>Empty / insufficient (&lt;5 rated)</Label>
            <BiasBar variant="mini" distGovt={{ pro: 100 }} ratedCount={2} />
          </div>
        </div>
        <p className="text-[12px]" style={{ color: "var(--pk-text-3)", lineHeight: 1.5 }}>
          Colorblind rule: percentages + labels always accompany color; the two &ldquo;lean&rdquo;
          segments carry a diagonal hatch, so five buckets are distinguishable without hue.
        </p>
      </Card>

      <Card id="chips" title="Rating chips + factuality dot">
        <div className="flex flex-col gap-2">
          <Label>Govt alignment — all buckets</Label>
          <div className="flex flex-wrap gap-2">
            {GOVT_BUCKETS.map((b) => (
              <RatingChip key={b.key} axis="govt" bucket={b.key} />
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <Label>Ideology — all buckets</Label>
          <div className="flex flex-wrap gap-2">
            {IDEOLOGY_BUCKETS.map((b) => (
              <RatingChip key={b.key} axis="ideology" bucket={b.key} />
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <Label>Pending · tiny (comparison rows) — label survives</Label>
          <div className="flex flex-wrap items-center gap-1.5">
            <RatingChip axis="govt" bucket="pending" />
            <RatingChip axis="govt" bucket="pro" size="tiny" short="Pro-est" />
            <RatingChip axis="govt" bucket="critical" size="tiny" />
            <RatingChip axis="ideology" bucket="left" size="tiny" />
            <RatingChip axis="ideology" bucket="right" size="tiny" />
            <span className="ml-2 flex items-center gap-1.5 text-[11px]" style={{ color: "var(--pk-text-3)" }}>
              {FACT_LEVELS.map((l) => (
                <FactualityDot key={l} level={l} />
              ))}
              ← factuality scale
            </span>
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <Label>Evidence popover (ⓘ trust surface) — click the ⓘ</Label>
          <EvidencePopover
            lastUpdated="May 2026"
            disputeHref="/dispute/ndtv"
            rows={[
              { stat: "52", text: "articles scored against the public rubric" },
              { stat: "3/3", text: "human panelists reviewed the LLM scoring" },
              { stat: "0.81", text: "inter-rater agreement (Krippendorff's α)" },
              { stat: "→", text: "full evidence table on the methodology page" },
            ]}
          >
            <RatingChip axis="govt" bucket="lean_pro" />
          </EvidencePopover>
        </div>
      </Card>

      <Card id="story-card" title="Story card" hint="full · Hindi + blindspot · compact 360 list">
        <div className="flex flex-wrap items-start gap-4">
          <StoryCard data={STORY_EN} />
          <StoryCard data={STORY_HI} />
          <div
            style={{
              width: 328,
              border: "1px solid var(--pk-border)",
              borderRadius: "var(--pk-r-md)",
              background: "var(--pk-surface)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "8px 14px",
                background: "var(--pk-surface-2)",
                fontFamily: "var(--pk-font-mono)",
                fontSize: 10,
                color: "var(--pk-text-3)",
              }}
            >
              compact · 360px list
            </div>
            {COMPACT.map((c, i) => (
              <StoryCard key={i} data={c} variant="compact" />
            ))}
          </div>
        </div>
      </Card>

      <Card id="ownership" title="Ownership card" hint="designed to screenshot">
        <OwnershipCard
          outletName="NDTV"
          chain={[
            { tier: "Outlet", name: "NDTV", note: "New Delhi Television Ltd" },
            { tier: "Media group", name: "AMG Media Networks", note: "acquired majority stake, Dec 2022" },
            { tier: "Ultimate owner", name: "Adani Group", note: "conglomerate — ports, energy, infrastructure" },
          ]}
          otherHoldings="Quintillion Business (BQ Prime) · IANS newswire"
          permalink="parakh.news/ndtv"
          onShareHref="/s/ndtv/share"
        />
      </Card>

      <Card id="fact-check" title="Fact-check chip" hint="verdict is the fact-checker's wording, quoted">
        <div className="flex flex-wrap gap-2">
          <FactCheckChip checker="Alt News" verdict="— claim misleading" href="https://example.org" />
          <FactCheckChip checker="BOOM" verdict="— partly false" href="https://example.org" />
        </div>
      </Card>

      <Card id="misc" title="Language toggle · blindspot badge">
        <div className="flex flex-wrap items-center gap-6">
          <LanguageToggle />
          <BlindspotBadge />
        </div>
        <p className="text-[12px]" style={{ color: "var(--pk-text-3)", lineHeight: 1.5 }}>
          हिंदी always set in Devanagari — never the word &ldquo;Hindi&rdquo;. Blindspot badge is a
          high-contrast neutral, never a pole color.
        </p>
      </Card>
    </main>
  );
}
