"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const NAV = [
  { href: "/", label: "Home" },
  { href: "/services/agentic-cost-governance", label: "Services" },
  { href: "/privacy", label: "Privacy" },
];

function navClass(active: boolean) {
  return active
    ? "text-slate-100"
    : "text-slate-400 hover:text-slate-100 transition-colors";
}

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-cyan-300">
          Noetfield
        </Link>

        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-md border border-slate-700 px-3 py-2 font-mono text-[0.65rem] uppercase tracking-wider text-slate-200 md:hidden"
          aria-expanded={open}
          aria-controls="site-primary-nav"
          onClick={() => setOpen((value) => !value)}
        >
          Menu
          <span className="sr-only">{open ? "Close navigation" : "Open navigation"}</span>
        </button>

        <nav
          id="site-primary-nav"
          aria-label="Primary"
          className={`${open ? "flex" : "hidden"} absolute left-0 right-0 top-full flex-col gap-3 border-b border-slate-800 bg-slate-950 px-6 py-4 md:static md:flex md:flex-row md:items-center md:gap-6 md:border-0 md:bg-transparent md:p-0`}
        >
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`text-sm ${navClass(pathname === item.href)}`}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
