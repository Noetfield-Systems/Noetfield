"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { LoadingBlock } from "@/components/LoadingBlock";
import { PageHero } from "@/components/PageHero";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { draftTle, listTles, TleSummary } from "@/lib/api";
import { wwwHref } from "@/lib/www-links";

function statusClass(status: string): string {
  if (status === "Approved") return "text-emerald-300";
  if (status === "Rejected") return "text-red-300";
  if (status === "Conditional") return "text-amber-300";
  return "text-muted";
}

export default function WorkspacePage() {
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [rows, setRows] = useState<TleSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [drafting, setDrafting] = useState(false);

  async function load(search?: string, status?: string) {
    setLoading(true);
    setError(null);
    try {
      setRows(
        await listTles({
          q: search,
          status: status || undefined,
        }),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load Trust Ledger.");
    } finally {
      setLoading(false);
    }
  }

  async function createDraft() {
    setDrafting(true);
    setError(null);
    try {
      const tle = await draftTle({
        evidence_ids: ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"],
      });
      window.location.href = `/workspace/${encodeURIComponent(tle.tle_id)}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create TLE draft.");
      setDrafting(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Shell active="workspace">
      <PageHero
        eyebrow="Trust Ledger v1"
        title="Trust Ledger Workspace"
        lead="Procurement-grade authorization records for Copilot adoption — evidence, confidence score, and approval chain."
      />

      <WorkflowStepper active="record" />

      <p className="mb-6 flex flex-wrap gap-x-4 gap-y-1 text-sm">
        <Link href="/workspace/connectors" className="text-accent hover:underline">
          M365 connectors (dev OAuth)
        </Link>
        <Link href={wwwHref("/copilot/demo/")} className="text-accent hover:underline">
          5-minute demo script
        </Link>
        <a href="/audit/export" className="text-accent hover:underline" download>
          Audit export (JSON)
        </a>
        <Link href={wwwHref("/copilot/procurement/")} className="text-accent hover:underline">
          Procurement buyer pack
        </Link>
      </p>

      <form
        className="nf-card mb-6 flex flex-wrap gap-3 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          load(q, statusFilter);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search TLE id, RID, decision…"
          className="nf-input min-w-[200px] flex-1"
          aria-label="Search Trust Ledger"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="nf-input"
          aria-label="Filter by status"
        >
          <option value="">All statuses</option>
          <option value="Draft">Draft</option>
          <option value="Approved">Approved</option>
          <option value="Conditional">Conditional</option>
          <option value="Rejected">Rejected</option>
        </select>
        <button type="submit" className="nf-btn-primary">
          Search
        </button>
        <button
          type="button"
          className="nf-btn-secondary"
          onClick={() => {
            setQ("");
            setStatusFilter("");
            load();
          }}
        >
          Reset
        </button>
      </form>

      <div className="mb-6 flex flex-wrap gap-3">
        <button type="button" className="nf-btn-primary" disabled={drafting} onClick={createDraft}>
          {drafting ? "Creating draft…" : "Create TLE draft from pilot evidence"}
        </button>
        <Link href={wwwHref("/trust-ledger/sample-report/")} className="nf-btn-secondary">
          TLE v1 samples (YAML)
        </Link>
      </div>

      {error && (
        <p
          className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          role="alert"
        >
          {error}
        </p>
      )}

      {loading && <LoadingBlock label="Loading Trust Ledger entries…" />}

      {!loading && rows.length === 0 && (
        <div className="nf-card p-8 text-center">
          <p className="text-muted">No Trust Ledger entries yet.</p>
          <p className="mt-2 text-sm text-muted-2">
            Create a draft from seeded pilot evidence or link from a governance evaluation.
          </p>
        </div>
      )}

      {!loading && rows.length > 0 && (
        <div className="nf-card overflow-x-auto">
          <table className="nf-data-table">
            <thead>
              <tr>
                <th>TLE ID</th>
                <th>Decision</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Date</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.tle_id}>
                  <td>
                    <code>{row.tle_id}</code>
                  </td>
                  <td className="max-w-xs text-white/90">{row.decision}</td>
                  <td>
                    <span
                      className="inline-flex rounded-full border border-accent/40 bg-accent/10 px-2.5 py-0.5 text-xs font-semibold text-accent"
                      aria-label={`Confidence ${(row.confidence_score * 100).toFixed(0)} percent`}
                    >
                      {(row.confidence_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className={`font-medium ${statusClass(row.status)}`}>{row.status}</td>
                  <td className="text-xs text-muted-2">
                    {row.date}
                    {row.source_rid ? (
                      <>
                        <br />
                        <span className="font-mono">RID {row.source_rid}</span>
                      </>
                    ) : null}
                  </td>
                  <td>
                    <Link
                      href={`/workspace/${encodeURIComponent(row.tle_id)}`}
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
