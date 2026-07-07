import type { Metadata, Viewport } from "next";
import { Noto_Sans, Noto_Sans_Devanagari, Noto_Sans_Mono } from "next/font/google";
import "./globals.css";

// Self-hosted at build by next/font, served locally with font-display: swap.
const notoSans = Noto_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto-sans",
  display: "swap",
});
const notoDevanagari = Noto_Sans_Devanagari({
  subsets: ["devanagari", "latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto-dev",
  display: "swap",
});
const notoMono = Noto_Sans_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-noto-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Parakh — Ground News for India",
    template: "%s · Parakh",
  },
  description:
    "See who's covering what — and who isn't. Coverage patterns, not truth-claims. No ads. No grants. No owner.",
  applicationName: "Parakh",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#FBFAF8" },
    { media: "(prefers-color-scheme: dark)", color: "#141312" },
  ],
  width: "device-width",
  initialScale: 1,
};

// Set the theme attribute before paint to avoid a flash. Defaults to the
// user's stored choice, else prefers-color-scheme (design contract).
const themeInit = `(function(){try{var t=localStorage.getItem('pk-theme');if(!t){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${notoSans.variable} ${notoDevanagari.variable} ${notoMono.variable}`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
