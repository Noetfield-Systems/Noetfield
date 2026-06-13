"use client";

import Link from "next/link";
import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { DevPortBanner } from "@/components/DevPortBanner";
import { MetricStrip } from "@/components/MetricStrip";
import { PolicyCallout } from "@/components/PolicyCallout";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { apiBaseLabel } from "@/lib/health";
import { platformConsoleHref } from "@/lib/platform-console";
import { useApiHealth } from "@/lib/useApiHealth";
import { wwwHref } from "@/lib/www-links";

export default function CognitiveDashboardPage() {
  const health = useApiHealth();

  return (
    <Shell active="dashboard">
      <DevPortBanner />
      <section className="mb-6">
        <p className="nf-eyebrow">Cognitive governance</p>
        <h2 className="mt-1 font-serif text-3xl font-semibold text-white">Cognitive dashboard</h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">
          Institutional sandbox for pre-execution intent evaluation — the same{" "}
          <strong className="text-white">Block · Record · Export</strong> path buyers see on{" "}
          <a href={wwwHref("/copilot/demo/")} className="text-accent hover:underline">
            noetfield.com
          </a>
          .
        </p>
      </section>

      <WorkflowStepper
        active="block"
        hrefs={{
          block: "/evaluate",
          record: "/workspace",
          export: wwwHref("/copilot/procurement/"),
        }}
      />

      <MetricStrip
        metrics={[
          {
            label: "Governance API",
            value: health?.ok ? "Operational" : health === null ? "Checking…" : "Offline",
            hint: apiBaseLabel(),
            tone: health?.ok ? "ok" : health === null ? "default" : "warn",
          },
          { label: "Demo path", value: "≤ 5 min", hint: "Evaluate → confidence → TLE export" },
          { label: "Evidence", value: "Metadata", hint: "Purview · Entra · audit index" },
          { label: "Design partner", value: "CAD $2K+", hint: "Board PDF in governance meeting" },
        ]}
      />

      <section
        className="nf-card mb-8 grid gap-3 border border-border bg-panel/80 p-5 sm:grid-cols-3"
        aria-label="Framework orientation"
      >
        <div>
          <p className="nf-eyebrow">NIST AI RMF</p>
          <p className="mt-1 text-sm font-semibold text-white">Govern · Manage</p>
          <p className="mt-1 text-xs text-muted-2">TLE export orientation — procurement ZIP</p>
        </div>
        <div>
          <p className="nf-eyebrow">Copilot complement</p>
          <p className="mt-1 text-sm font-semibold text-white">Registry vs receipt</p>
          <p className="mt-1 text-xs text-muted-2">
            <a href={wwwHref("/copilot/")} className="text-accent hover:underline">
              Agent 365 + Purview complement
            </a>
          </p>
        </div>
        <div>
          <p className="nf-eyebrow">Trust center</p>
          <p className="mt-1 text-sm font-semibold text-white">Control checkpoints</p>
          <p className="mt-1 text-xs text-muted-2">
            <a href={wwwHref("/trust-center/")} className="text-accent hover:underline">
              Framework diligence grid
            </a>
          </p>
        </div>
      </section>

      <PolicyCallout tag="OSFI E-23" title="Shadow evidence for model-risk committees" tone="info">
        <p>
          Use Bank Pilot mode for FRFI diligence — evaluate intent, record RID lineage, export TLE for board
          packs. Execution stays in your licensed environment.
        </p>
      </PolicyCallout>

      <section
        className="mb-8 rounded-xl border border-accent/30 bg-accent/5 p-6"
        aria-label="5-minute demo"
      >
        <p className="nf-eyebrow">5-minute demo</p>
        <h3 className="mt-1 text-lg font-semibold text-white">Evaluate → confidence score → Trust Ledger</h3>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Submit intent below, open the result RID, and show the <strong className="text-white">confidence score</strong>{" "}
          badge. Continue in{" "}
          <Link href="/workspace" className="text-accent hover:underline">
            Workspace
          </Link>{" "}
          for TLE PDF export.
        </p>
        <p className="mt-3 text-sm">
          <Link href={wwwHref("/copilot/demo/")} className="text-accent hover:underline">
            Locked demo script →
          </Link>
        </p>
      </section>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link href="/audit" className="nf-card-hover block p-4">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-2">Compliance</p>
          <p className="mt-2 text-lg font-medium text-white">Audit log</p>
          <p className="mt-1 text-sm text-muted-2">Search evaluations by RID</p>
        </Link>
        <Link href="/workspace" className="nf-card-hover block p-4">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-2">Trust Ledger</p>
          <p className="mt-2 text-lg font-medium text-white">TLE workspace</p>
          <p className="mt-1 text-sm text-muted-2">Approvals · PDF · procurement ZIP</p>
        </Link>
        <Link href="/workspace/connectors" className="nf-card-hover block p-4">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-2">Connectors</p>
          <p className="mt-2 text-lg font-medium text-white">M365 evidence</p>
          <p className="mt-1 text-sm text-muted-2">Register + mock connect</p>
        </Link>
        <a href={platformConsoleHref()} className="nf-card-hover block p-4">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-2">Platform API</p>
          <p className="mt-2 text-lg font-medium text-white">Legacy console</p>
          <p className="mt-1 text-sm text-muted-2">Port 8001 evaluate shell</p>
        </a>
      </div>

      <section className="nf-card p-6">
        <h3 className="mb-1 text-lg font-semibold text-white">Submit operational intent</h3>
        <p className="mb-4 text-sm text-muted-2">Pre-execution evaluation — policy fires before external execution.</p>
        <EvaluateForm />
      </section>
    </Shell>
  );
}
