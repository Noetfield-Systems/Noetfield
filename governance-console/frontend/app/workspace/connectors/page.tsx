"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { LoadingBlock } from "@/components/LoadingBlock";
import { MetricStrip } from "@/components/MetricStrip";
import { PageHero } from "@/components/PageHero";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { listConnectors, registerConnector, ConnectorSummary } from "@/lib/api";

function formatSync(lastSync?: string | null): string {
  if (!lastSync) return "Never";
  try {
    return new Date(lastSync).toLocaleString();
  } catch {
    return "—";
  }
}

function statusTone(status: string, connected: boolean): "default" | "ok" | "warn" {
  if (connected && status === "connected") return "ok";
  if (status === "registered") return "warn";
  return "default";
}

export default function ConnectorsPage() {
  const [rows, setRows] = useState<ConnectorSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [registering, setRegistering] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setRows(await listConnectors());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load connectors.");
    } finally {
      setLoading(false);
    }
  }

  async function registerM365() {
    setRegistering(true);
    setError(null);
    try {
      const id = `m365-purview-${Date.now()}`;
      await registerConnector({
        connector_id: id,
        connector_type: "m365_purview",
        required_scopes: ["Purview.Read", "AuditLog.Read"],
      });
      window.location.href = `/connectors/${encodeURIComponent(id)}/oauth/start`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed.");
      setRegistering(false);
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const connected = params.get("connected");
    if (connected) setSuccess(connected);
    load();
  }, []);

  const connectedCount = rows.filter((c) => c.oauth_connected).length;

  return (
    <Shell active="connectors">
      <Breadcrumbs
        items={[
          { label: "Workspace", href: "/workspace" },
          { label: "M365 connectors" },
        ]}
      />

      <PageHero
        eyebrow="Evidence index"
        title="M365 evidence connectors"
        lead="Complement Agent 365 and Purview with metadata-only evidence ingest. Local dev uses mock OAuth — Last sync visible after connect."
      />

      <WorkflowStepper
        active="record"
        hrefs={{
          block: "/evaluate",
          export: "/workspace",
        }}
      />

      <MetricStrip
        metrics={[
          { label: "Connectors", value: loading ? "…" : String(rows.length), hint: "Registered in tenant" },
          {
            label: "OAuth",
            value: loading ? "…" : String(connectedCount),
            hint: "Mock-connected",
            tone: connectedCount > 0 ? "ok" : "default",
          },
          { label: "Ingest", value: "Metadata", hint: "No content hoarding" },
          { label: "Agent 365", value: "Complement", hint: "Registry vs receipt" },
        ]}
      />

      {success && (
        <p
          className="mb-4 rounded-lg border border-emerald-900/80 bg-emerald-950/40 px-4 py-3 text-sm text-emerald-200"
          role="status"
        >
          Mock OAuth connected — <code>{success}</code>. M365 evidence ingested.
        </p>
      )}
      {error && (
        <p className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200" role="alert">
          {error}
        </p>
      )}

      <div className="mb-6 flex flex-wrap gap-3">
        <button type="button" className="nf-btn-primary" disabled={registering} onClick={() => registerM365()}>
          {registering ? "Registering…" : "Register + mock connect (M365)"}
        </button>
        <Link href="/workspace" className="nf-btn-secondary">
          Trust Ledger Workspace
        </Link>
      </div>

      {loading && <LoadingBlock label="Loading connectors…" />}

      {!loading && (
        <div className="nf-card overflow-x-auto">
          <table className="nf-data-table">
            <thead>
              <tr>
                <th>Connector ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>OAuth</th>
                <th>Last sync</th>
                <th>Scopes</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-sm text-muted-2">
                    No connectors registered — use Register + mock connect above.
                  </td>
                </tr>
              ) : (
                rows.map((c) => (
                  <tr key={c.connector_id}>
                    <td>
                      <code>{c.connector_id}</code>
                    </td>
                    <td>{c.connector_type}</td>
                    <td>
                      <span className={`nf-status-pill nf-status-pill-${statusTone(c.status, c.oauth_connected)}`}>
                        {c.status}
                      </span>
                    </td>
                    <td>{c.oauth_connected ? "Connected" : "Pending"}</td>
                    <td className="text-xs text-muted-2">{formatSync(c.last_sync)}</td>
                    <td className="max-w-[200px] text-xs text-muted-2">
                      {(c.required_scopes ?? []).join(", ") || "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </Shell>
  );
}
