import type { Metadata } from "next";
import { ThemeToggle } from "@/components/ThemeToggle";
import { StoryCard, StoryCardData } from "@/components/StoryCard";

export const metadata: Metadata = { title: "Mixed-script render test" };

/**
 * M0 acceptance surface: the design-system "side-by-side test" — Latin and
 * Devanagari as first-class scripts, at every type-scale step, in one mixed
 * list. Verify by eye: matra headroom (line-height +0.15 on Devanagari),
 * no letter-spacing on Devanagari, matched sizes, baseline sanity.
 */

const SCALE: { name: string; token: string; en: string; hi: string }[] = [
  { name: "Display (mobile)", token: "600 28px/1.25", en: "Data protection rules notified", hi: "डेटा संरक्षण नियम अधिसूचित" },
  { name: "Title", token: "600 20px/1.35", en: "Industry seeks a six-month transition", hi: "उद्योग ने छह महीने का समय मांगा" },
  { name: "Headline", token: "500 16px/1.45", en: "Centre notifies rules; brokers react", hi: "केंद्र ने नियम अधिसूचित किए; ब्रोकरों की प्रतिक्रिया" },
  { name: "Body", token: "400 15px/1.55", en: "Coverage patterns, not truth-claims — we show who covered a story and who did not.", hi: "कवरेज पैटर्न, सत्य-दावे नहीं — हम दिखाते हैं कि किसने खबर को कवर किया और किसने नहीं।" },
  { name: "Caption", token: "400 13px/1.45", en: "34 outlets · 2h ago", hi: "34 आउटलेट · 2 घंटे पहले" },
];

// A single list that interleaves scripts — the specific case the design flags.
const MIXED: StoryCardData[] = [
  { title: "SEBI proposes tighter F&O disclosure norms for retail brokers", outletCount: 18, timeAgo: "4h", distGovt: { pro: 45, mixed: 40, critical: 15 }, ratedCount: 18 },
  { title: "रेलवे ने तीन नई वंदे भारत स्लीपर ट्रेनों की घोषणा की", lang: "hi", outletCount: 26, timeAgo: "1h", distGovt: { pro: 70, mixed: 25, critical: 5 }, ratedCount: 26 },
  { title: "Supreme Court to hear electoral bonds review petitions next week", outletCount: 22, timeAgo: "3h", distGovt: { pro: 30, mixed: 40, critical: 30 }, ratedCount: 22 },
  { title: "किसान संगठनों ने एमएसपी पर कानूनी गारंटी की मांग दोहराई", lang: "hi", outletCount: 14, timeAgo: "5h", distGovt: { pro: 25, mixed: 45, critical: 30 }, ratedCount: 14 },
];

function scaleParts(token: string) {
  // "600 28px/1.25" -> weight, size, lh
  const [weightSize, lh] = token.split("/");
  const [weight, size] = weightSize.split(" ");
  return { weight, size, lh: Number(lh) };
}

export default function MixedScriptTest() {
  return (
    <main
      style={{ minHeight: "100dvh", background: "var(--pk-bg)" }}
      className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-10"
    >
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-[24px] font-semibold" style={{ color: "var(--pk-text)" }}>
            Mixed-script render test
          </h1>
          <p className="text-[13px]" style={{ color: "var(--pk-text-3)" }}>
            English + हिंदी as first-class scripts · pass criteria below
          </p>
        </div>
        <ThemeToggle />
      </header>

      <ul
        className="text-[13px]"
        style={{
          background: "var(--pk-surface)",
          border: "1px solid var(--pk-border)",
          borderRadius: "var(--pk-r-md)",
          padding: "14px 18px 14px 34px",
          color: "var(--pk-text-2)",
          lineHeight: 1.7,
          listStyle: "disc",
        }}
      >
        <li>Devanagari matra stack has headroom (line-height +0.15) — no clipping of top/bottom marks.</li>
        <li>Devanagari is never letter-spaced.</li>
        <li>Latin and Devanagari share the same size at each scale step.</li>
        <li>A single list mixing both scripts stays visually even (no jumpy baselines).</li>
      </ul>

      <section
        className="flex flex-col"
        style={{
          background: "var(--pk-surface)",
          border: "1px solid var(--pk-border)",
          borderRadius: "var(--pk-r-lg)",
          overflow: "hidden",
        }}
      >
        {SCALE.map((row, i) => {
          const p = scaleParts(row.token);
          return (
            <div
              key={row.name}
              className="grid"
              style={{
                gridTemplateColumns: "150px 1fr 1fr",
                gap: 20,
                padding: "16px 20px",
                borderTop: i === 0 ? "none" : "1px solid var(--pk-border)",
                alignItems: "baseline",
              }}
            >
              <div className="flex flex-col gap-1">
                <div className="text-[13px] font-semibold" style={{ color: "var(--pk-text)" }}>
                  {row.name}
                </div>
                <div style={{ fontFamily: "var(--pk-font-mono)", fontSize: 11, color: "var(--pk-text-3)" }}>
                  {row.token}
                </div>
              </div>
              <div
                style={{
                  fontFamily: "var(--pk-font-ui)",
                  fontWeight: Number(p.weight),
                  fontSize: p.size,
                  lineHeight: p.lh,
                  color: "var(--pk-text)",
                }}
              >
                {row.en}
              </div>
              <div
                lang="hi"
                style={{
                  fontFamily: "var(--pk-font-dev)",
                  fontWeight: Number(p.weight),
                  fontSize: p.size,
                  lineHeight: p.lh + 0.15,
                  letterSpacing: "normal",
                  color: "var(--pk-text)",
                }}
              >
                {row.hi}
              </div>
            </div>
          );
        })}
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-[16px] font-semibold" style={{ color: "var(--pk-text)" }}>
          Mixed-script feed list
        </h2>
        <div
          style={{
            border: "1px solid var(--pk-border)",
            borderRadius: "var(--pk-r-lg)",
            background: "var(--pk-surface)",
            overflow: "hidden",
          }}
        >
          {MIXED.map((c, i) => (
            <StoryCard key={i} data={c} variant="compact" />
          ))}
        </div>
      </section>
    </main>
  );
}
