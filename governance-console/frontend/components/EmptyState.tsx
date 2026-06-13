import Link from "next/link";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: { label: string; href: string };
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="nf-empty-state nf-card p-10 text-center">
      <p className="font-serif text-lg font-semibold text-white">{title}</p>
      <p className="mx-auto mt-2 max-w-md text-sm text-muted-2">{description}</p>
      {action && (
        <Link href={action.href} className="nf-btn-primary mt-6 inline-flex text-sm">
          {action.label}
        </Link>
      )}
    </div>
  );
}
