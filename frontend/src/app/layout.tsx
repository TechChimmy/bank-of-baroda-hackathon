import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "../components/Header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Secure Auth Demo",
  description: "Phishing-resistant MFA & detection (Hackathon MVP)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="min-h-dvh bg-gradient-to-b from-neutral-950 via-neutral-950 to-black text-white">
          <Header />
          <main className="mx-auto max-w-5xl px-4 py-8">
            {children}
          </main>
          <footer className="mt-8 border-t border-neutral-800/60">
            <div className="mx-auto max-w-5xl px-4 py-6 text-sm text-neutral-400">
              <span>© {new Date().getFullYear()} Secure Auth Demo</span>
              <span className="mx-2">•</span>
              <span>For hackathon demo purposes only</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
