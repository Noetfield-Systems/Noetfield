"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { DecisionBadge } from "@/components/DecisionBadge";
import { EmptyState } from "@/components/EmptyState";
import { LoadingBlock } from "@/components/LoadingBlock";
import { MetricStrip } from "@/components/MetricStrip";
import { PageHero } from "@/components/PageHero";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { AuditRecord, listAudit } from "@/lib/api";

export default function AuditPage() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<AuditRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load(search?: string) {
    setLoading(true);
    setError(null);
    try {
      setRows(await listAudit(search));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load audit log.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const allowCount = rows.filter((r) => r.decision.toLowerCase() === "allow").length;
  const denyCount = rows.filter((r) => r.decision.toLowerCase() === "deny").length;

  return (
    <Shell active="audit">
      <PageHero
        eyebrow="Compliance"
        title="Audit log"
        lead="Every evaluation is stored with a unique RID for immutable compliance traceability — the same evidence spine examiners expect from pre-execution governance."
      />

      <WorkflowStepper active="record" hrefs={{ block: "/evaluate", export: "/workspace" }} />

      <MetricStrip
        metrics={[
          { label: "Events", value: loading ? "…" : String(rows.length), hint: "Current tenant view" },
          { label: "Allowed", value: loading ? "…" : String(allowCount), tone: "ok" },
          { label: "Denied", value: loading ? "…" : String(denyCount), tone: denyCount > 0 ? "warn" : "default" },
          { label: "Export", value: "JSON", hint: "Diligence bundle download" },
        ]}
      />

      <div
        className="nf-card mb-8 flex flex-wrap items-center justify-between gap-4 border border-accent/30 bg-accent/5 p-6"
        role="region"
        aria-label="Audit export bundle"
      >
        <div>
          <p className="nf-eyebrow">Diligence export</p>
          <p className="mt-1 text-sm text-white/90">
            Download JSON bundle for engagement intake — includes{" "}
            <strong>{loading ? "…" : rows.length}</strong> event{rows.length === 1 ? "" : "s"} in current
            view (tenant: pilot default).
          </p>
          <p className="mt-1 text-xs text-muted-2">
            Board packs use TLE export from{" "}
            <Link href="/workspace" className="text-accent hover:underline">
              Workspace
            </Link>
            .
          </p>
        </div>
        <a href="/audit/export" className="nf-btn-primary shrink-0" download>
          Export bundle (JSON)
        </a>
      </div>

      <form
        className="nf-card mb-6 flex flex-wrap gap-3 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          load(q);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by RID, actor, or action…"
          className="nf-input min-w-[240px] flex-1"
          aria-label="Search audit log"
        />
        <button type="submit" className="nf-btn-primary">
          Search
        </button>
        <button
          type="button"
          onClick={() => {
            setQ("");
            load();
          }}
          className="nf-btn-secondary"
        >
          Reset
        </button>
      </form>

      {error && (
        <p
          className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          role="alert"
        >
          {error}
        </p>
      )}

      {loading && <LoadingBlock label="Loading audit records…" />}

      {!loading && rows.length === 0 && (
        <EmptyState
          title="No evaluations yet"
          description="Submit operational intent to generate your first immutable RID receipt."
          action={{ label: "Evaluate intent →", href: "/evaluate" }}
        />
      )}

      {!loading && rows.length > 0 && (
        <div className="nf-card overflow-x-auto">
          <table className="nf-data-table">
            <thead>
              <tr>
                <th>RID</th>
                <th>Decision</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Risk</th>
                <th>Timestamp</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.rid}>
                  <td>
                    <code>{row.rid}</code>
                  </td>
                  <td>
                    <DecisionBadge decision={row.decision} />
                  </td>
                  <td className="max-w-[140px] truncate text-white/90" title={row.actor}>
                    {row.actor}
                  </td>
                  <td className="max-w-[160px] truncate" title={row.action}>
                    {row.action}
                  </td>
                  <td>
                    <span className="font-mono text-xs">{row.risk_score}</span>
                  </td>
                  <td className="text-xs text-muted-2">{new Date(row.timestamp).toLocaleString()}</td>
                  <td>
                    <Link
                      href={`/result/${encodeURIComponent(row.rid)}`}
                      className="text-sm text-accent hover:underline"
                    >
                      Open →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Shell>
  );
}
