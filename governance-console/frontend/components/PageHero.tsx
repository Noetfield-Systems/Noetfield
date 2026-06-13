type PageHeroProps = {
  eyebrow: string;
  title: string;
  lead: string;
};

export function PageHero({ eyebrow, title, lead }: PageHeroProps) {
  return (
    <section className="nf-institutional-hero mb-10 rounded-xl border border-accent/25 p-6 sm:p-8">
      <p className="nf-eyebrow">{eyebrow}</p>
      <h2 className="mt-2 font-serif text-3xl font-semibold tracking-tight text-white sm:text-4xl">{title}</h2>
      <p className="mt-3 max-w-2xl text-base leading-relaxed text-muted">{lead}</p>
    </section>
  );
}
