import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Google Places Scraper - Professional Data Extraction",
  description: "Extract business data from Google Places with our powerful scraping tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <div className="bg-gradient-effect"></div>
        <div className="bg-grid-effect"></div>
        <div className="container mx-auto max-w-[1400px] p-4 md:p-8">
          {children}
        </div>
      </body>
    </html>
  );
}
