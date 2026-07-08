import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Notice | Noetfield",
  description: "How Noetfield handles information on noetfield.com.",
};

export default function PrivacyPage() {
  return (
    <main id="main-content" className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      <section className="mx-auto max-w-3xl">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Legal // v1.0</p>
        <h1 className="mt-6 text-4xl font-semibold tracking-tight">Privacy Notice</h1>
        <p className="mt-4 text-lg text-slate-300">
          What we collect on noetfield.com, why, and the choices available to you.
        </p>

        <div className="legal-copy mt-10 max-w-none">
          <h2>Scope</h2>
          <p>
            This notice applies to the public marketing site at noetfield.com. Product consoles, APIs, and
            partner programs may have separate terms hosted on their own domains.
          </p>

          <h2>Information we process</h2>
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Purpose</th>
                <th>Retention</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Essential cookies / local storage</td>
                <td>Remember cookie preferences</td>
                <td>Until you clear browser storage</td>
              </tr>
              <tr>
                <td>Server access logs</td>
                <td>Security and reliability</td>
                <td>Short operational retention</td>
              </tr>
              <tr>
                <td>Contact requests you initiate</td>
                <td>Respond to inbound inquiries</td>
                <td>Per operational workflow</td>
              </tr>
            </tbody>
          </table>

          <p>
            We do not sell personal information. Analytics cookies are <strong>off by default</strong> until you opt
            in through the cookie banner.
          </p>

          <h2>Your choices</h2>
          <p>
            Use <Link href="/cookies">Cookie preferences</Link> in the site footer at any time. For privacy
            questions, contact <a href="mailto:operations@noetfield.com">operations@noetfield.com</a>.
          </p>

          <h2>Updates</h2>
          <p>We update this page when site functionality changes. Check the version marker above for the current revision.</p>
        </div>
      </section>
    </main>
  );
}
