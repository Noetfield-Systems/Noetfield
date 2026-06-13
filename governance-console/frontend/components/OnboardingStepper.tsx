"use client";

import Link from "next/link";
import { wwwHref } from "@/lib/www-links";

const STEPS = [
  { n: 1, title: "Start sandbox", href: wwwHref("/copilot/trial/"), external: true },
  { n: 2, title: "Evaluate intent", href: "/evaluate", external: false },
  { n: 3, title: "Connect evidence", href: "/workspace/connectors", external: false },
  { n: 4, title: "Draft TLE", href: "/workspace", external: false },
  { n: 5, title: "Export board PDF", href: wwwHref("/copilot/procurement/"), external: true },
] as const;

export function OnboardingStepper() {
  return (
    <section
      className="nf-card mb-6 border border-border bg-panel/60 p-4"
      aria-label="Async demo onboarding"
    >
      <p className="nf-eyebrow">Full async demo</p>
      <h3 className="mt-1 text-sm font-semibold text-white">5-step path — no sales call</h3>
      <ol className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        {STEPS.map((step) => (
          <li key={step.n}>
            {step.external ? (
              <a
                href={step.href}
                className="flex items-center gap-2 rounded-lg border border-border/80 bg-surface/50 px-3 py-2 text-xs hover:border-accent/40"
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent/40 text-[10px] font-bold text-accent">
                  {step.n}
                </span>
                <span className="text-muted">{step.title}</span>
              </a>
            ) : (
              <Link
                href={step.href}
                className="flex items-center gap-2 rounded-lg border border-border/80 bg-surface/50 px-3 py-2 text-xs hover:border-accent/40"
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent/40 text-[10px] font-bold text-accent">
                  {step.n}
                </span>
                <span className="text-muted">{step.title}</span>
              </Link>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
