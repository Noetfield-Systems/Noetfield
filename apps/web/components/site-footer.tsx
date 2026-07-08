"use client";

import Link from "next/link";
import { openCookiePreferences } from "../lib/cookie-consent";

export function SiteFooter() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="mx-auto flex max-w-5xl flex-col gap-4 px-6 py-8 text-xs text-slate-500 md:flex-row md:items-center md:justify-between">
        <p className="font-mono uppercase tracking-[0.12em]">Noetfield Systems Inc.</p>
        <nav aria-label="Legal" className="flex flex-wrap gap-4">
          <Link href="/privacy" className="hover:text-slate-300 transition-colors">
            Privacy
          </Link>
          <Link href="/cookies" className="hover:text-slate-300 transition-colors">
            Cookies
          </Link>
          <button
            type="button"
            className="hover:text-slate-300 transition-colors"
            onClick={() => openCookiePreferences()}
          >
            Cookie preferences
          </button>
        </nav>
      </div>
    </footer>
  );
}
