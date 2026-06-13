"use client";

import Link from "next/link";
import { wwwHref } from "@/lib/www-links";

const TRIAL_DAYS = 14;
const TRIAL_CHECKS = 50;

export function TrialBanner() {
  return (
    <div
      className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-accent/30 bg-accent/5 px-4 py-3 text-sm"
      role="status"
      aria-label="Starter tier trial"
    >
      <div>
        <p className="font-semibold text-white">
          Starter tier · Free dev sandbox
        </p>
        <p className="text-xs text-muted-2">
          {TRIAL_DAYS}-day trial · {TRIAL_CHECKS} evaluate checks · full async demo
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3 text-xs">
        <span className="rounded-full border border-border px-2 py-1 text-muted">
          Tier: <strong className="text-accent">Starter</strong>
        </span>
        <a href={wwwHref("/copilot/trial/")} className="text-accent hover:underline">
          Trial details
        </a>
        <Link href="/evaluate" className="rounded-lg bg-accent/20 px-3 py-1.5 font-medium text-accent hover:bg-accent/30">
          Start evaluate
        </Link>
      </div>
    </div>
  );
}
