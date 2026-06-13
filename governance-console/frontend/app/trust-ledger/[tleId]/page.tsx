"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { LoadingBlock } from "@/components/LoadingBlock";
import { MetricStrip } from "@/components/MetricStrip";
import { PageHero } from "@/components/PageHero";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { exportTlePdfUrl, formatConfidence, getTle, TrustLedgerEntry } from "@/lib/trustLedger";
import { wwwHref } from "@/lib/www-links";

export default function TrustLedgerDetailPage() {
  const params = useParams();
  const tleId = typeof params.tleId === "string" ? params.tleId : "";
  const [entry, setEntry] = useState<TrustLedgerEntry | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tleId) return;
    setLoading(true);
    setError(null);
    getTle(tleId)
      .then(setEntry)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load TLE."))
      .finally(() => setLoading(false));
  }, [tleId]);

  const confidencePct =
    entry?.confidence_score !== undefined ? `${Math.round(entry.confidence_score * 100)}%` : "—";

  return (
    <Shell active="trust-ledger">
      <Breadcrumbs
        items={[
          { label: "Trust Ledger", href: "/trust-ledger" },
          { label: tleId || "…" },
        ]}
      />

      {loading && <LoadingBlock label="Loading TLE…" />}

      {error && (
        <p className="rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200" role="alert">
          {error}
        </p>
      )}

      {entry && (
        <>
          <PageHero
            eyebrow={entry.tle_id}
            title={entry.decision ?? "Trust Ledger Entry"}
            lead={`Status ${entry.status}${entry.date ? ` · ${entry.date}` : ""} — procurement-grade go/no-go record.`}
          />

          <WorkflowStepper active="export" hrefs={{ block: "/evaluate", record: "/trust-ledger" }} />

          <MetricStrip
            metrics={[
              { label: "Confidence", value: confidencePct, hint: "Board PDF cover", tone: "ok" },
              { label: "Status", value: entry.status, hint: "Approval workflow" },
              { label: "Evidence", value: String(entry.evidence?.length ?? 0), hint: "Metadata index" },
              { label: "Export", value: "PDF", hint: "When approved" },
            ]}
          />

          {entry.confidence_score !== undefined && (
            <div
              className="nf-card mb-8 flex flex-wrap items-center justify-between gap-4 border border-accent/30 bg-accent/5 p-6"
              role="status"
              aria-label="Confidence score"
            >
              <div>
                <p className="nf-eyebrow">Confidence score</p>
                <p className="font-serif text-4xl font-semibold text-accent">{formatConfidence(entry.confidence_score)}</p>
                {entry.confidence_method && (
                  <p className="mt-1 text-sm text-muted-2">Method: {entry.confidence_method}</p>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                <Link href={wwwHref("/copilot/demo/")} className="nf-btn-secondary text-sm">
                  Demo script
                </Link>
                <Link href="/workspace" className="nf-btn-secondary text-sm">
                  Workspace approvals
                </Link>
              </div>
            </div>
          )}

          {entry.confidence_factors && entry.confidence_factors.length > 0 && (
            <section className="nf-card mb-8 p-5">
              <h3 className="text-sm font-medium uppercase text-muted">Score factors</h3>
              <ul className="mt-4 space-y-2 text-sm text-muted">
                {entry.confidence_factors.map((f) => (
                  <li key={f.factor} className="flex flex-wrap justify-between gap-2 border-t border-border/60 pt-2">
                    <span>
                      <strong className="text-white">{f.factor}</strong> — {f.detail}
                    </span>
                    <span className="font-mono text-accent">+{Math.round(f.contribution * 100)}%</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <div className="mb-8 grid gap-4 sm:grid-cols-2">
            <div className="nf-card p-5">
              <h3 className="text-sm font-medium text-muted">Export</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                <a className="nf-btn-secondary text-sm" href={`/tle/${encodeURIComponent(tleId)}/export`}>
                  Board pack (JSON)
                </a>
                <a
                  className="nf-btn-secondary text-sm"
                  href={`/tle/${encodeURIComponent(tleId)}/export?format=html`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Board pack (HTML)
                </a>
                <a
                  className="nf-btn-secondary text-sm"
                  href={`/tle/${encodeURIComponent(tleId)}/export?format=pdf`}
                  download
                >
                  Board pack (PDF)
                </a>
                <a
                  className="nf-btn-secondary text-sm"
                  href={`/tle/${encodeURIComponent(tleId)}/export?format=zip`}
                  download
                >
                  Procurement pack (ZIP)
                </a>
              </div>
            </div>
            <div className="nf-card p-5">
              <h3 className="text-sm font-medium text-muted">Diligence</h3>
              <p className="mt-2 text-sm text-muted-2">
                Approved entries export tamper-evident board PDF and procurement ZIP for legal review.
              </p>
              {entry.status === "Approved" && (
                <a
                  href={exportTlePdfUrl(tleId)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="nf-btn-primary mt-4 inline-flex text-sm"
                >
                  Download board pack (PDF)
                </a>
              )}
            </div>
          </div>

          {entry.evidence && entry.evidence.length > 0 && (
            <section className="mb-8">
              <h3 className="mb-3 font-serif text-xl text-white">Evidence ({entry.evidence.length})</h3>
              <ul className="space-y-2">
                {entry.evidence.map((ev, i) => (
                  <li key={i} className="nf-card p-4 text-sm">
                    <span className="font-mono text-accent">
                      {(ev as { evidence_id?: string }).evidence_id ?? "ev"}
                    </span>
                    <span className="text-muted-2"> · </span>
                    {(ev as { title?: string }).title ?? ""}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {entry.approval_chain && entry.approval_chain.length > 0 && (
            <section>
              <h3 className="mb-3 font-serif text-xl text-white">Approval chain</h3>
              <ul className="space-y-3">
                {entry.approval_chain.map((step, i) => (
                  <li key={i} className="nf-card p-4 text-sm">
                    <span className="font-medium text-white">
                      {(step as { approver?: { id?: string; name?: string } }).approver?.name ??
                        (step as { approver?: { id?: string } }).approver?.id ??
                        "approver"}
                    </span>
                    <span className="text-muted-2"> · </span>
                    {(step as { status?: string }).status}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </Shell>
  );
}
