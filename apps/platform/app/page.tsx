const layers = [
  "Raw signals",
  "Normalized intelligence",
  "Living knowledge graph",
  "Governance ledger",
  "Cognitive memory",
  "Operational runtime",
];

export default function PlatformPage() {
  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-14 text-zinc-100">
      <section className="mx-auto max-w-6xl">
        <p className="text-sm uppercase tracking-[0.3em] text-emerald-300">Platform</p>
        <h1 className="mt-6 text-4xl font-semibold">Governed intelligence command layer</h1>
        <p className="mt-5 max-w-3xl text-zinc-300">
          This app shell will host AI inventory, signal ingestion, graph intelligence,
          workflows, human reviews, and ledger-backed audit views.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {layers.map((layer) => (
            <div key={layer} className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
              {layer}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
