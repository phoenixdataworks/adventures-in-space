import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Arcade Games Collection",
  description: "A collection of retro-style arcade games built with Pygame",
  keywords: ["arcade", "games", "pygame", "retro", "web games"],
  authors: [{ name: "Arcade Games" }],
  openGraph: {
    title: "Arcade Games Collection",
    description: "Play retro-style arcade games in your browser",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="scanlines">
        {children}
      </body>
    </html>
  );
}

