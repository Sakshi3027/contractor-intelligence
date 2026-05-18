import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Contractor Intelligence",
  description: "Agentic lead intelligence system for IT contractor partners",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}