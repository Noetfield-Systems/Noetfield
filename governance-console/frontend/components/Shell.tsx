"use client";

import Link from "next/link";
import { Footer } from "@/components/Footer";
import { useApiHealth } from "@/lib/useApiHealth";
import { wwwHref } from "@/lib/www-links";

type ShellProps = {
  children: React.ReactNode;
  active?: "dashboard" | "evaluate" | "audit" | "trust-ledger" | "workspace" | "connectors";
};

function navClass(active: boolean): string {
  return `rounded-lg px-3 py-2 text-sm transition hover:bg-white/5${active ? " bg-white/10 font-medium text-white ring-1 ring-accent/25" : " text-muted"}`;
}

export function Shell({ children, active }: ShellProps) {
  const health = useApiHealth();

  return (
    <div className="min-h-screen flex flex-col">
      <div className="border-b border-border/80 bg-surface/90 text-xs text-muted-2">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-2">
          <span>
            <strong className="text-muted">Institutional site 2026</strong> · Shadow mode · Pre-execution governance · No
            custody or payments
          </span>
          <span className="flex flex-wrap items-center gap-3">
            <a href={wwwHref("/trust-center/")} className="text-accent hover:underline">
              Trust center
            </a>
            <a href={wwwHref("/")} className="hover:text-white">
              noetfield.com
            </a>
            <a href={wwwHref("/copilot/procurement/")} className="hover:text-white">
              Procurement pack
            </a>
            <span aria-live="polite">
              API{" "}
              {health === null ? (
                <span className="text-muted">…</span>
              ) : health.ok ? (
                <span className="text-ok">● operational</span>
              ) : (
                <span className="text-red-300">● offline</span>
              )}
            </span>
          </span>
        </div>
      </div>
      <header className="sticky top-0 z-20 border-b border-border bg-panel/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4">
          <Link href="/cognitive-dashboard" className="flex items-center gap-3 hover:opacity-90">
            <img
              src="/noetfield-favicon-512.png"
              alt=""
              width={40}
              height={40}
              className="rounded-lg ring-1 ring-border"
            />
            <div>
              <p className="nf-eyebrow">Noetfield Systems</p>
              <h1 className="font-serif text-lg font-semibold text-white">Governance Console</h1>
              <p className="text-[11px] text-muted-2">Block · Record · Export</p>
            </div>
          </Link>
          <nav className="flex flex-wrap gap-1" aria-label="Console navigation">
            <Link href="/cognitive-dashboard" className={navClass(active === "dashboard")}>
              Dashboard
            </Link>
            <Link href="/evaluate" className={navClass(active === "evaluate")}>
              Evaluate
            </Link>
            <Link href="/audit" className={navClass(active === "audit")}>
              Audit log
            </Link>
            <Link href="/trust-ledger" className={navClass(active === "trust-ledger")}>
              Trust Ledger
            </Link>
            <Link href="/workspace" className={navClass(active === "workspace")}>
              Workspace
            </Link>
            <Link href="/workspace/connectors" className={navClass(active === "connectors")}>
              Connectors
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">{children}</main>
      <Footer />
    </div>
  );
}
