export const COOKIE_CONSENT_KEY = "noetfield_cookie_consent_v1";

export type CookieConsent = {
  version: 1;
  essential: boolean;
  analytics: boolean;
  updatedAt: string;
};

export const COOKIE_PREFERENCES_EVENT = "noetfield:open-cookie-preferences";

export function defaultConsent(analytics: boolean): CookieConsent {
  return {
    version: 1,
    essential: true,
    analytics,
    updatedAt: new Date().toISOString(),
  };
}

export function readConsent(): CookieConsent | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as CookieConsent;
    if (parsed.version !== 1 || typeof parsed.essential !== "boolean") return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeConsent(consent: CookieConsent): void {
  localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(consent));
  document.documentElement.dataset.analytics = consent.analytics ? "granted" : "denied";
}

export function openCookiePreferences(): void {
  window.dispatchEvent(new CustomEvent(COOKIE_PREFERENCES_EVENT));
}
