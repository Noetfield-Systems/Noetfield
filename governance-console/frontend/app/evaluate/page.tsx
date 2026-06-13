"use client";

import Link from "next/link";
import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { MetricStrip } from "@/components/MetricStrip";
import { PageHero } from "@/components/PageHero";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { wwwHref } from "@/lib/www-links";

export default function EvaluatePage() {
  return (
    <Shell active="evaluate">
      <PageHero
        eyebrow="Pre-execution"
        title="Submit operational intent"
        lead="Describe who is acting, what they propose, and the operational context. Noetfield returns a governance decision before any external system executes."
      />

      <WorkflowStepper
        active="block"
        hrefs={{
          record: "/workspace",
          export: wwwHref("/copilot/procurement/"),
        }}
      />

      <MetricStrip
        metrics={[
          { label: "Decision path", value: "< 2 sec", hint: "Evaluate → RID → confidence score" },
          { label: "Receipt", value: "Immutable", hint: "Every evaluation stored with RID" },
          { label: "Policy mode", value: "Pre-exec", hint: "BLOCK before M365 or partners act" },
          { label: "Demo", value: "5 min", hint: "Board-ready confidence badge" },
        ]}
      />

      <section
        className="nf-card mb-8 border border-accent/30 bg-accent/5 p-6"
        aria-label="5-minute demo"
      >
        <p className="nf-eyebrow">Institutional demo</p>
        <h3 className="mt-1 text-lg font-semibold text-white">Show confidence in the governance meeting</h3>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Submit a realistic Copilot intent below, open the result RID, and highlight the{" "}
          <strong className="text-white">confidence score</strong> badge. Continue to{" "}
          <Link href="/workspace" className="text-accent hover:underline">
            Workspace
          </Link>{" "}
          for TLE export.
        </p>
        <p className="mt-3 text-sm">
          <Link href={wwwHref("/copilot/demo/")} className="text-accent hover:underline">
            Locked demo script →
          </Link>
        </p>
      </section>

      <EvaluateForm />
    </Shell>
  );
}
