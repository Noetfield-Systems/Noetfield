type PolicyCalloutTone = "fence" | "info" | "ok";

type PolicyCalloutProps = {
  tag?: string;
  title: string;
  children: React.ReactNode;
  tone?: PolicyCalloutTone;
};

const toneClass: Record<PolicyCalloutTone, string> = {
  fence: "border-accent/40 bg-accent/5",
  info: "border-blue-400/35 bg-blue-400/5",
  ok: "border-ok/35 bg-ok/5",
};

export function PolicyCallout({ tag, title, children, tone = "fence" }: PolicyCalloutProps) {
  return (
    <aside
      className={`nf-policy-callout mb-8 rounded-xl border p-5 ${toneClass[tone]}`}
      aria-label={title}
    >
      {tag ? <p className="nf-eyebrow">{tag}</p> : null}
      <h3 className="mt-1 text-base font-semibold text-white">{title}</h3>
      <div className="mt-2 text-sm leading-relaxed text-muted">{children}</div>
    </aside>
  );
}
