import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hebrew-Chinese Bible Research Fixture Shell",
  description: "P1-VS-001 release-pinned passage serving shell using canonical fixtures.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
