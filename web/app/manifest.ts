import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Parakh — Ground News for India",
    short_name: "Parakh",
    description:
      "See who's covering what — and who isn't. Coverage patterns, not truth-claims.",
    start_url: "/",
    display: "standalone",
    background_color: "#FBFAF8",
    theme_color: "#0E8583",
    icons: [
      // Full icon set ships from Auxiliary Screens 9e (M3).
      { src: "/icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any" },
    ],
  };
}
