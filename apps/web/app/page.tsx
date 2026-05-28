const principles = [
  "Workflow-first governance",
  "Append-only auditability",
  "Living knowledge graph memory",
  "Human-governed intelligence execution",
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      <section className="mx-auto max-w-5xl">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Noetfield v3.1</p>
        <h1 className="mt-6 text-5xl font-semibold tracking-tight">
          Autonomous Governed Intelligence Nervous System
        </h1>
        <p className="mt-6 max-w-3xl text-lg text-slate-300">
          Ambient market intelligence infrastructure built around governance memory,
          event-centric orchestration, and human-reviewed AI execution.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {principles.map((principle) => (
            <div key={principle} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              {principle}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
