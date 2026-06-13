type Metric = {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "ok" | "warn";
};

type MetricStripProps = {
  metrics: Metric[];
};

export function MetricStrip({ metrics }: MetricStripProps) {
  return (
    <div className="nf-metrics mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" role="list">
      {metrics.map((m) => (
        <div
          key={m.label}
          className={`nf-metrics-item${m.tone === "ok" ? " nf-metrics-ok" : ""}${m.tone === "warn" ? " nf-metrics-warn" : ""}`}
          role="listitem"
        >
          <p className="nf-metrics-label">{m.label}</p>
          <p className="nf-metrics-value">{m.value}</p>
          {m.hint && <p className="nf-metrics-hint">{m.hint}</p>}
        </div>
      ))}
    </div>
  );
}
