import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wildlife Scanner - SDG 15: Life on Land",
  description:
    "Scan animals to learn about their conservation status and how protecting them connects to UN Sustainable Development Goal 15.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
