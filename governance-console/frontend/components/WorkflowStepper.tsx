import Link from "next/link";

const STEPS = [
  { id: "block", label: "Block", detail: "Invalid intent rejected pre-execution" },
  { id: "record", label: "Record", detail: "Signed TLE + RID audit lineage" },
  { id: "export", label: "Export", detail: "Board PDF · procurement ZIP" },
] as const;

type WorkflowStepperProps = {
  active?: "block" | "record" | "export";
  hrefs?: Partial<Record<(typeof STEPS)[number]["id"], string>>;
};

export function WorkflowStepper({ active, hrefs }: WorkflowStepperProps) {
  return (
    <div
      className="nf-pipeline mb-8 grid gap-3 sm:grid-cols-3"
      role="list"
      aria-label="Governance execution pipeline"
    >
      {STEPS.map((step, i) => {
        const isActive = active === step.id;
        const href = hrefs?.[step.id];
        const inner = (
          <>
            <span className="nf-pipeline-num" aria-hidden="true">
              {i + 1}
            </span>
            <span className="nf-pipeline-label">{step.label}</span>
            <span className="nf-pipeline-detail">{step.detail}</span>
          </>
        );
        const className = `nf-pipeline-step${isActive ? " nf-pipeline-step-active" : ""}`;
        if (href) {
          return (
            <Link key={step.id} href={href} className={className} role="listitem">
              {inner}
            </Link>
          );
        }
        return (
          <div key={step.id} className={className} role="listitem">
            {inner}
          </div>
        );
      })}
    </div>
  );
}
