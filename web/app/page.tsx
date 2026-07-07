import Link from "next/link";
import { ParallaxMark } from "@/components/ParallaxMark";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function Home() {
  return (
    <main
      style={{ minHeight: "100dvh", background: "var(--pk-bg)" }}
      className="mx-auto flex max-w-3xl flex-col gap-10 px-6 py-12"
    >
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <ParallaxMark size={30} />
          <span className="text-[20px] font-semibold" style={{ color: "var(--pk-text)" }}>
            Parakh
          </span>
          <span
            lang="hi"
            className="text-[15px]"
            style={{ fontFamily: "var(--pk-font-dev)", color: "var(--pk-text-3)" }}
          >
            परख
          </span>
        </div>
        <ThemeToggle />
      </header>

      <section className="flex flex-col gap-4">
        <h1
          className="text-[36px] font-semibold"
          style={{ lineHeight: 1.2, color: "var(--pk-text)", letterSpacing: "-0.01em" }}
        >
          See who&rsquo;s covering what — and who isn&rsquo;t.
        </h1>
        <p className="text-[15px]" style={{ lineHeight: 1.55, color: "var(--pk-text-2)", maxWidth: 560 }}>
          Parakh clusters coverage of the same story across Indian outlets and shows the
          coverage distribution across a dual bias axis, blindspots, factuality, and
          ownership. <strong style={{ color: "var(--pk-text)" }}>We show coverage patterns,
          not truth-claims.</strong>
        </p>
        <p
          className="text-[13px] font-semibold uppercase"
          style={{ letterSpacing: "0.06em", color: "var(--pk-brand)" }}
        >
          No ads · No grants · No owner
        </p>
      </section>

      <section
        className="flex flex-col gap-3"
        style={{
          background: "var(--pk-surface)",
          border: "1px solid var(--pk-border)",
          borderRadius: "var(--pk-r-lg)",
          padding: 22,
        }}
      >
        <div className="text-[12px] font-semibold uppercase" style={{ letterSpacing: "0.05em", color: "var(--pk-text-3)" }}>
          M0 skeleton — build surfaces
        </div>
        <nav className="flex flex-col gap-2">
          <Link href="/styleguide" style={{ color: "var(--pk-brand)", fontWeight: 600 }}>
            → Component gallery (design-system primitives, light + dark)
          </Link>
          <Link href="/mixed-script-test" style={{ color: "var(--pk-brand)", fontWeight: 600 }}>
            → Mixed-script render test (English + हिंदी)
          </Link>
        </nav>
      </section>
    </main>
  );
}
