import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cookie Policy | Noetfield",
  description: "Cookie categories used on noetfield.com.",
};

export default function CookiesPage() {
  return (
    <main id="main-content" className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      <section className="mx-auto max-w-3xl">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Legal // v1.0</p>
        <h1 className="mt-6 text-4xl font-semibold tracking-tight">Cookie Policy</h1>
        <p className="mt-4 text-lg text-slate-300">Essential storage only by default — analytics is optional.</p>

        <div className="legal-copy mt-10 max-w-none">
          <h2>Essential (always on)</h2>
          <p>Required to remember your cookie choice while using this site.</p>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Storage</th>
                <th>Duration</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>noetfield_cookie_consent_v1</code>
                </td>
                <td>localStorage</td>
                <td>Until cleared</td>
                <td>Stores your consent decision</td>
              </tr>
            </tbody>
          </table>

          <h2>Analytics (optional)</h2>
          <p>
            If you opt in, we may enable privacy-respecting usage measurement on this domain in the future.{" "}
            <strong>No third-party analytics scripts are loaded today.</strong>
          </p>

          <h2>Managing preferences</h2>
          <p>
            Open <Link href="/privacy">Privacy</Link> for context, or use the footer control labeled{" "}
            <strong>Cookie preferences</strong> on any page.
          </p>
        </div>
      </section>
    </main>
  );
}
