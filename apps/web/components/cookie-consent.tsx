"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  COOKIE_PREFERENCES_EVENT,
  defaultConsent,
  readConsent,
  writeConsent,
  type CookieConsent,
} from "../lib/cookie-consent";

export function CookieConsent() {
  const [bannerOpen, setBannerOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [analytics, setAnalytics] = useState(false);

  useEffect(() => {
    const existing = readConsent();
    if (existing) {
      writeConsent(existing);
      setAnalytics(existing.analytics);
      setBannerOpen(false);
    } else {
      setBannerOpen(true);
    }

    const onPreferences = () => {
      const current = readConsent() ?? defaultConsent(false);
      setAnalytics(current.analytics);
      setModalOpen(true);
    };

    window.addEventListener(COOKIE_PREFERENCES_EVENT, onPreferences);
    return () => window.removeEventListener(COOKIE_PREFERENCES_EVENT, onPreferences);
  }, []);

  function persist(consent: CookieConsent) {
    writeConsent(consent);
    setAnalytics(consent.analytics);
    setBannerOpen(false);
    setModalOpen(false);
  }

  return (
    <>
      {bannerOpen ? (
        <div
          role="dialog"
          aria-labelledby="cookie-banner-title"
          aria-describedby="cookie-banner-desc"
          className="fixed inset-x-0 bottom-0 z-50 border-t border-slate-800 bg-slate-950/95 p-4 backdrop-blur-md"
        >
          <div className="mx-auto flex max-w-5xl flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p id="cookie-banner-title" className="text-sm font-semibold text-slate-100">
                Cookie preferences
              </p>
              <p id="cookie-banner-desc" className="mt-1 max-w-2xl text-sm text-slate-400">
                We use essential storage to remember your choices. Optional analytics stays off unless you opt in.{" "}
                <Link href="/cookies" className="text-cyan-300 underline-offset-2 hover:underline">
                  Learn more
                </Link>
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded-md border border-slate-700 px-3 py-2 font-mono text-[0.65rem] uppercase tracking-wider text-slate-200"
                onClick={() => persist(defaultConsent(false))}
              >
                Reject non-essential
              </button>
              <button
                type="button"
                className="rounded-md border border-slate-700 px-3 py-2 font-mono text-[0.65rem] uppercase tracking-wider text-slate-200"
                onClick={() => {
                  const current = readConsent() ?? defaultConsent(false);
                  setAnalytics(current.analytics);
                  setModalOpen(true);
                }}
              >
                Customize
              </button>
              <button
                type="button"
                className="rounded-md border border-cyan-600 px-3 py-2 font-mono text-[0.65rem] uppercase tracking-wider text-cyan-300 hover:bg-cyan-300 hover:text-slate-950 transition-colors"
                onClick={() => persist(defaultConsent(true))}
              >
                Accept all
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {modalOpen ? (
        <div className="fixed inset-0 z-[60] grid place-items-center p-4" role="presentation">
          <button
            type="button"
            aria-label="Close cookie preferences"
            className="absolute inset-0 bg-black/60"
            onClick={() => setModalOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="cookie-modal-title"
            className="relative w-full max-w-md border border-slate-800 bg-slate-900 p-6 shadow-2xl"
          >
            <h2 id="cookie-modal-title" className="text-lg font-semibold text-slate-100">
              Cookie preferences
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Choose optional categories. Essential storage is required for this site to remember your consent.
            </p>

            <div className="mt-4 space-y-3">
              <div className="rounded-lg border border-slate-800 p-4 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <strong className="text-slate-200">Essential</strong>
                  <span className="font-mono text-[0.65rem] uppercase tracking-wider text-slate-500">Always on</span>
                </div>
                <p className="mt-2 text-slate-400">Stores your consent decision in this browser.</p>
              </div>

              <label className="block rounded-lg border border-slate-800 p-4 text-sm cursor-pointer">
                <div className="flex items-center justify-between gap-3">
                  <strong className="text-slate-200">Analytics</strong>
                  <input
                    type="checkbox"
                    checked={analytics}
                    onChange={(event) => setAnalytics(event.target.checked)}
                    className="h-4 w-4 rounded border-slate-600 bg-slate-950 text-cyan-400"
                  />
                </div>
                <p className="mt-2 text-slate-400">
                  Optional usage measurement on noetfield.com. No third-party analytics scripts are loaded today.
                </p>
              </label>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                className="rounded-md border border-slate-700 px-3 py-2 font-mono text-[0.65rem] uppercase tracking-wider text-slate-200"
                onClick={() => setModalOpen(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="rounded-md border border-cyan-600 px-3 py-2 font-mono text-[0.65rem] uppercase tracking-wider text-cyan-300 hover:bg-cyan-300 hover:text-slate-950 transition-colors"
                onClick={() => persist(defaultConsent(analytics))}
              >
                Save preferences
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
