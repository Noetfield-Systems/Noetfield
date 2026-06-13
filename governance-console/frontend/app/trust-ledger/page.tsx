"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { EmptyState } from "@/components/EmptyState";
import { LoadingBlock } from "@/components/LoadingBlock";
import { MetricStrip } from "@/components/MetricStrip";
import { PageHero } from "@/components/PageHero";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { formatConfidence, listTles, TrustLedgerEntry } from "@/lib/trustLedger";
import { wwwHref } from "@/lib/www-links";

function statusClass(status: string): string {
  if (status === "Approved") return "text-emerald-300";
  if (status === "Rejected") return "text-red-300";
  if (status === "PendingApproval") return "text-amber-300";
  return "text-muted";
}

export default function TrustLedgerListPage() {
  const [status, setStatus] = useState("");
  const [rows, setRows] = useState<TrustLedgerEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load(filter?: string) {
    setLoading(true);
    setError(null);
    try {
      const res = await listTles(filter || undefined);
      setRows(res.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load Trust Ledger entries.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const approved = rows.filter((r) => r.status === "Approved").length;

  return (
    <Shell active="trust-ledger">
      <PageHero
        eyebrow="Trust Ledger v1"
        title="Trust Ledger"
        lead="Read-only institutional view of Trust Ledger Entries — signed go/no-go records with confidence score for procurement sign-off."
      />

      <WorkflowStepper
        active="record"
        hrefs={{
          block: "/evaluate",
          export: wwwHref("/copilot/procurement/"),
        }}
      />

      <MetricStrip
        metrics={[
          { label: "Entries", value: loading ? "…" : String(rows.length), hint: "TLE v1 records" },
          { label: "Approved", value: loading ? "…" : String(approved), tone: approved > 0 ? "ok" : "default" },
          { label: "Evidence", value: "Metadata", hint: "Compliance · identity · audit index" },
          { label: "Export", value: "PDF + ZIP", hint: "Board pack · procurement pack" },
        ]}
      />

      <div className="mb-6 flex flex-wrap gap-3">
        <Link href="/trust-ledger/new" className="nf-btn-primary">
          New TLE draft
        </Link>
        <Link href="/workspace" className="nf-btn-secondary">
          Workspace (approvals)
        </Link>
        <Link href={wwwHref("/trust-ledger/sample-report/")} className="nf-btn-secondary">
          TLE samples
        </Link>
      </div>

      <form
        className="nf-card mb-6 flex flex-wrap gap-3 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          load(status);
        }}
      >
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="nf-input"
          aria-label="Filter by status"
        >
          <option value="">All statuses</option>
          <option value="PendingApproval">Pending approval</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
          <option value="Draft">Draft</option>
        </select>
        <button type="submit" className="nf-btn-primary">
          Filter
        </button>
        <button
          type="button"
          onClick={() => {
            setStatus("");
            load();
          }}
          className="nf-btn-secondary"
        >
          Reset
        </button>
      </form>

      {error && (
        <p className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200" role="alert">
          {error}
        </p>
      )}

      {loading && <LoadingBlock label="Loading Trust Ledger entries…" />}

      {!loading && rows.length === 0 && (
        <EmptyState
          title="No Trust Ledger entries yet"
          description="Create a draft or run tle-smoke to seed sample entries for procurement review."
          action={{ label: "Create TLE draft →", href: "/trust-ledger/new" }}
        />
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
                <th />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.tle_id}>
                  <td>
                    <code>{row.tle_id}</code>
                  </td>
                  <td className="max-w-xs text-white/90">{row.decision ?? "—"}</td>
                  <td>
                    {row.confidence_score !== undefined ? (
                      <span className="nf-status-pill nf-status-pill-accent">
                        {formatConfidence(row.confidence_score)}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className={`font-medium ${statusClass(row.status)}`}>{row.status}</td>
                  <td>
                    <Link
                      href={`/trust-ledger/${encodeURIComponent(row.tle_id)}`}
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
