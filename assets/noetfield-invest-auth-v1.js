/**
 * Noetfield investor auth — Supabase portfolio-spine (Google · email · magic link).
 * Config: /assets/noetfield-platform-auth-config-v1.json
 */
(function (global) {
  "use strict";

  const CONFIG_URL = "/assets/noetfield-platform-auth-config-v1.json";
  const SUPABASE_CDN = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js";
  const INVEST_SESSION_API = "/api/auth/invest-session";

  let config = null;
  let client = null;

  function $(id) {
    return document.getElementById(id);
  }

  function showStatus(el, text, kind) {
    if (!el) return;
    el.textContent = text || "";
    el.hidden = !text;
    el.classList.toggle("is-error", kind === "error");
    el.classList.toggle("is-ok", kind === "ok");
  }

  function friendlyAuthError(err) {
    const msg = String((err && (err.message || err.error_description || err.msg)) || err || "");
    if (/redirect_uri|redirect url/i.test(msg)) {
      return "OAuth redirect mismatch — add www.noetfield.com callback URLs in Supabase.";
    }
    if (/provider is not enabled/i.test(msg)) {
      return "Google sign-in is not enabled in Supabase yet.";
    }
    if (/invalid login credentials/i.test(msg)) {
      return "Email or password is wrong.";
    }
    return msg || "Sign-in failed";
  }

  function callbackUrl() {
    return global.location.origin + "/auth/callback/";
  }

  function signInUrl(nextPath) {
    const next = nextPath || global.location.pathname + global.location.search;
    if (!next || next.indexOf("/auth/sign-in") === 0) return "/auth/sign-in/";
    return "/auth/sign-in/?next=" + encodeURIComponent(next);
  }

  function redirectToSignIn(nextPath) {
    global.location.replace(signInUrl(nextPath));
  }

  function clearAuthParamsFromUrl() {
    const u = new URL(global.location.href);
    ["code", "error", "error_code", "error_description"].forEach(function (k) {
      u.searchParams.delete(k);
    });
    global.history.replaceState(null, "", u.pathname + (u.searchParams.toString() ? "?" + u.searchParams.toString() : ""));
    if (global.location.hash && (global.location.hash.includes("access_token") || global.location.hash.includes("error"))) {
      global.history.replaceState(null, "", u.pathname + u.search);
    }
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (global.supabase && global.supabase.createClient) {
        resolve();
        return;
      }
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = function () {
        resolve();
      };
      s.onerror = function () {
        reject(new Error("Failed to load Supabase client"));
      };
      document.head.appendChild(s);
    });
  }

  async function loadConfig() {
    if (config) return config;
    const res = await fetch(CONFIG_URL, { cache: "no-store" });
    if (!res.ok) throw new Error("Auth config missing");
    config = await res.json();
    return config;
  }

  async function getClient() {
    if (client) return client;
    const cfg = await loadConfig();
    if (!cfg.configured || !cfg.supabase_url || !cfg.supabase_anon_key) {
      throw new Error("Investor sign-in is not configured yet.");
    }
    await loadScript(SUPABASE_CDN);
    client = global.supabase.createClient(cfg.supabase_url, cfg.supabase_anon_key, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
        flowType: "pkce",
      },
    });
    return client;
  }

  async function getSession() {
    const sb = await getClient();
    const row = await sb.auth.getSession();
    if (row.error) throw row.error;
    return row.data && row.data.session;
  }

  async function setInvestCookie(session) {
    if (!session || !session.access_token) return false;
    const res = await fetch(INVEST_SESSION_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ access_token: session.access_token }),
    });
    return res.ok;
  }

  async function syncInvestCookie() {
    const session = await getSession();
    if (!session) return false;
    return setInvestCookie(session);
  }

  async function consumeOAuthCallback(sb) {
    const params = new URLSearchParams(global.location.search || "");
    const code = params.get("code");
    if (code) {
      const row = await sb.auth.exchangeCodeForSession(code);
      if (row.error) throw row.error;
      clearAuthParamsFromUrl();
      return row.data && row.data.session;
    }
    if ((global.location.hash || "").includes("access_token")) {
      const row = await sb.auth.getSession();
      clearAuthParamsFromUrl();
      return row.data && row.data.session;
    }
    return null;
  }

  function routeAfterSignIn() {
    const params = new URLSearchParams(global.location.search || "");
    const next = params.get("next");
    if (next && next.startsWith("/") && next.indexOf("//") === -1) {
      global.location.href = next;
      return;
    }
    global.location.href = "/invest/";
  }

  async function signInWithOAuth(provider) {
    const sb = await getClient();
    const row = await sb.auth.signInWithOAuth({
      provider: provider,
      options: {
        redirectTo: callbackUrl(),
        queryParams: { venture: "noetfield" },
      },
    });
    if (row.error) throw row.error;
  }

  async function signInWithPassword(email, password) {
    const sb = await getClient();
    const row = await sb.auth.signInWithPassword({ email: email, password: password });
    if (row.error) throw row.error;
    const session = row.data && row.data.session;
    if (!session) throw new Error("Sign in failed");
    await setInvestCookie(session);
    routeAfterSignIn();
  }

  async function signInWithMagicLink(email) {
    const sb = await getClient();
    const row = await sb.auth.signInWithOtp({
      email: email,
      options: { emailRedirectTo: callbackUrl(), shouldCreateUser: false },
    });
    if (row.error) throw row.error;
  }

  async function signOut() {
    try {
      const sb = await getClient();
      await sb.auth.signOut();
    } catch (_) {
      /* quiet */
    }
    await fetch("/api/auth/invest-sign-out", { method: "POST", credentials: "same-origin" }).catch(function () {});
    client = null;
    global.location.href = "/";
  }

  async function guardInvestPage(onReady) {
    const gate = $("nf-invest-gate");
    try {
      const sb = await getClient();
      await consumeOAuthCallback(sb);
      const session = await getSession();
      if (!session) {
        redirectToSignIn("/invest/");
        return;
      }
      const ok = await setInvestCookie(session);
      if (!ok) {
        if (gate) gate.textContent = "Could not establish secure session. Try signing in again.";
        return;
      }
      if (gate) gate.hidden = true;
      const app = $("nf-invest-app");
      if (app) app.hidden = false;
      if (typeof onReady === "function") onReady(session);
    } catch (e) {
      if (gate) gate.textContent = friendlyAuthError(e);
    }
  }

  async function bootSignInPage() {
    const status = $("nf-auth-status");
    const form = $("nf-auth-signin-form");
    const google = $("nf-auth-google");

    try {
      await loadConfig();
      const urlErr = new URLSearchParams(global.location.search).get("error_description");
      if (urlErr) showStatus(status, friendlyAuthError(urlErr), "error");

      const sb = await getClient();
      const existing = await getSession();
      if (existing) {
        await setInvestCookie(existing);
        routeAfterSignIn();
        return;
      }
    } catch (e) {
      showStatus(status, friendlyAuthError(e), "error");
      if (google) google.disabled = true;
      return;
    }

    if (google) {
      google.addEventListener("click", function () {
        showStatus(status, "Redirecting to Google…", "ok");
        signInWithOAuth("google").catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }

    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        const email = ($("nf-auth-email") || {}).value.trim();
        const password = ($("nf-auth-password") || {}).value || "";
        if (!email || !password) return;
        showStatus(status, "Signing in…", "ok");
        signInWithPassword(email, password).catch(function (e) {
          showStatus(status, friendlyAuthError(e), "error");
        });
      });
    }

    const magic = $("nf-auth-magic");
    if (magic) {
      magic.addEventListener("click", function (ev) {
        ev.preventDefault();
        const email = ($("nf-auth-email") || {}).value.trim();
        if (!email) {
          showStatus(status, "Enter your email first.", "error");
          return;
        }
        showStatus(status, "Sending magic link…", "ok");
        signInWithMagicLink(email)
          .then(function () {
            showStatus(status, "Check your email for the sign-in link.", "ok");
          })
          .catch(function (e) {
            showStatus(status, friendlyAuthError(e), "error");
          });
      });
    }
  }

  async function bootCallbackPage() {
    const status = $("nf-auth-callback-status");
    try {
      const sb = await getClient();
      const session = await consumeOAuthCallback(sb) || (await getSession());
      if (!session) throw new Error("No session — try signing in again.");
      await setInvestCookie(session);
      if (status) status.textContent = "Signed in. Redirecting…";
      routeAfterSignIn();
    } catch (e) {
      if (status) status.textContent = friendlyAuthError(e);
      setTimeout(function () {
        redirectToSignIn("/invest/");
      }, 2500);
    }
  }

  global.NoetfieldInvestAuth = {
    getClient: getClient,
    getSession: getSession,
    guardInvestPage: guardInvestPage,
    bootSignInPage: bootSignInPage,
    bootCallbackPage: bootCallbackPage,
    signOut: signOut,
    syncInvestCookie: syncInvestCookie,
    signInUrl: signInUrl,
  };
})(typeof window !== "undefined" ? window : globalThis);
