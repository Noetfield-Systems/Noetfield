import Link from "next/link";
import { wwwHref } from "@/lib/www-links";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-border bg-surface/40 py-10">
      <div className="mx-auto max-w-6xl px-4">
        <div className="flex flex-wrap items-start justify-between gap-8">
          <div className="max-w-sm">
            <p className="nf-eyebrow">Noetfield Systems</p>
            <p className="mt-2 text-sm leading-relaxed text-muted-2">
              Pre-execution governance · Block · Record · Export · No custody or payments
            </p>
            <p className="mt-3 text-xs text-muted-2">
              <a href={wwwHref("/")} className="text-accent hover:underline">
                noetfield.com
              </a>
              {" · "}
              <a href={wwwHref("/copilot/procurement/")} className="hover:text-accent">
                Procurement pack
              </a>
            </p>
          </div>
          <nav className="flex flex-wrap gap-x-8 gap-y-4 text-sm text-muted-2" aria-label="Footer">
            <div>
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted">Console</p>
              <ul className="space-y-2">
                <li>
                  <Link href="/cognitive-dashboard" className="hover:text-accent">
                    Dashboard
                  </Link>
                </li>
                <li>
                  <Link href="/evaluate" className="hover:text-accent">
                    Evaluate
                  </Link>
                </li>
                <li>
                  <Link href="/audit" className="hover:text-accent">
                    Audit log
                  </Link>
                </li>
                <li>
                  <Link href="/workspace" className="hover:text-accent">
                    Workspace
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted">Buyer</p>
              <ul className="space-y-2">
                <li>
                  <a href={wwwHref("/copilot/demo/")} className="hover:text-accent">
                    5-minute demo
                  </a>
                </li>
                <li>
                  <a href={wwwHref("/trust-center/")} className="hover:text-accent">
                    Trust center
                  </a>
                </li>
                <li>
                  <a href={wwwHref("/trust-ledger/sample-report/")} className="hover:text-accent">
                    TLE samples
                  </a>
                </li>
              </ul>
            </div>
          </nav>
        </div>
      </div>
    </footer>
  );
}
