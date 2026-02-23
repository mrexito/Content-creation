import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { NavBar } from "@/components/nav-bar";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LangChain vs LangGraph – Thesis Demo",
  description: "Master Thesis: Automated Content Rewriting Comparison",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-slate-700 text-slate-50`}
      >
        <NavBar />
        <main className="container mx-auto px-4 py-8 max-w-7xl">
          {children}
        </main>
        <Toaster richColors theme="dark" />
      </body>
    </html>
  );
}
