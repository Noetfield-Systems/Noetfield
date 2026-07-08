import type { Metadata, Viewport } from "next";
import { CookieConsent } from "../components/cookie-consent";
import { SiteFooter } from "../components/site-footer";
import { SiteHeader } from "../components/site-header";
import { SkipLink } from "../components/skip-link";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Noetfield",
    template: "%s | Noetfield",
  },
  description: "AI trust infrastructure for governed ambient intelligence.",
  metadataBase: new URL("https://www.noetfield.com"),
  openGraph: {
    type: "website",
    locale: "en_CA",
    siteName: "Noetfield",
    title: "Noetfield",
    description: "AI trust infrastructure for governed ambient intelligence.",
  },
};

export const viewport: Viewport = {
  themeColor: "#020617",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <SkipLink />
        <SiteHeader />
        {children}
        <SiteFooter />
        <CookieConsent />
      </body>
    </html>
  );
}
