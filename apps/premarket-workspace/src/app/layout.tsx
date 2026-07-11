import "@fontsource-variable/ibm-plex-sans";
import "@fontsource/ibm-plex-mono/400.css";
import "./globals.css";

import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "A-Share Premarket Workspace",
  description: "Local research-only position management and market evidence workspace",
};

export default function RootLayout({children}: Readonly<{children: ReactNode}>) {
  return <html lang="en"><body>{children}</body></html>;
}
