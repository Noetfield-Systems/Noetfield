const controls = [
  "Tenants",
  "Identity providers",
  "RBAC and ABAC",
  "Policy bundles",
  "Model providers",
  "Audit exports",
];

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-neutral-950 px-6 py-14 text-neutral-100">
      <section className="mx-auto max-w-6xl">
        <p className="text-sm uppercase tracking-[0.3em] text-amber-300">Admin</p>
        <h1 className="mt-6 text-4xl font-semibold">Enterprise governance control plane</h1>
        <p className="mt-5 max-w-3xl text-neutral-300">
          This app shell will manage tenant isolation, identity, policy, provider,
          retention, and observability configuration.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {controls.map((control) => (
            <div key={control} className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
              {control}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
