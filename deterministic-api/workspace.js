/* Deterministic API workspace client — talks to det-api Worker only (not Company New). */
(function () {
  const API = "https://nf-deterministic-api-v1.sina-kazemnezhad-ca.workers.dev";
  const SESSION_KEY = "nf_dapi_session";
  let lastRawKey = "";

  function $(sel) {
    return document.querySelector(sel);
  }

  function errMsg(data, fallback) {
    if (!data) return fallback;
    if (typeof data.error === "object" && data.error && data.error.message) return data.error.message;
    if (typeof data.error === "string") return data.error;
    if (data.message) return data.message;
    if (data.detail) return data.detail;
    return fallback;
  }

  function setStatus(el, msg, kind) {
    if (!el) return;
    el.textContent = msg || "";
    el.classList.toggle("is-error", kind === "is-error");
    el.classList.toggle("is-ok", kind === "is-ok");
  }

  function getSession() {
    try {
      return sessionStorage.getItem(SESSION_KEY) || "";
    } catch {
      return "";
    }
  }

  function setSession(token) {
    try {
      if (token) sessionStorage.setItem(SESSION_KEY, token);
      else sessionStorage.removeItem(SESSION_KEY);
    } catch {
      /* ignore */
    }
  }

  function absorbHashSession() {
    const hash = location.hash.replace(/^#/, "");
    if (!hash.startsWith("session=")) return;
    const token = decodeURIComponent(hash.slice("session=".length));
    if (token) {
      setSession(token);
      history.replaceState(null, "", location.pathname + location.search);
    }
  }

  async function api(path, opts = {}) {
    const headers = Object.assign({ "content-type": "application/json" }, opts.headers || {});
    const token = getSession();
    if (token) headers.authorization = `Bearer ${token}`;
    const res = await fetch(`${API}${path}`, Object.assign({}, opts, { headers }));
    const data = await res.json().catch(() => ({}));
    return { res, data };
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if ([...document.scripts].some((s) => s.src === src)) {
        resolve();
        return;
      }
      const el = document.createElement("script");
      el.src = src;
      el.async = true;
      el.onload = () => resolve();
      el.onerror = () => reject(new Error("Could not load Google sign-in"));
      document.head.appendChild(el);
    });
  }

  async function copyText(text) {
    if (!text) return false;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch {
      /* fall through */
    }
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch {
      ok = false;
    }
    document.body.removeChild(ta);
    return ok;
  }

  async function signInWithGoogle(cfg, statusEl) {
    const clientId = cfg.google_client_id;
    if (!clientId) throw new Error("Google sign-in is not configured");
    setStatus(statusEl, "Opening Google…");
    await loadScript("https://accounts.google.com/gsi/client");
    if (!window.google?.accounts?.oauth2?.initTokenClient) {
      throw new Error("Google sign-in unavailable");
    }
    await new Promise((resolve, reject) => {
      let settled = false;
      const done = (err) => {
        if (settled) return;
        settled = true;
        if (err) reject(err);
        else resolve();
      };
      const tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: "openid email profile",
        callback: async (tokenResponse) => {
          try {
            if (tokenResponse?.error) {
              throw new Error(tokenResponse.error_description || tokenResponse.error);
            }
            if (!tokenResponse?.access_token) throw new Error("No Google access token returned");
            setStatus(statusEl, "Verifying Google…");
            const { res, data } = await api("/v1/customer-auth/google", {
              method: "POST",
              body: JSON.stringify({ access_token: tokenResponse.access_token }),
            });
            if (!res.ok || !data.ok || !data.session_token) {
              throw new Error(errMsg(data, "Google verification failed"));
            }
            setSession(data.session_token);
            const next = new URLSearchParams(location.search).get("next") || "/deterministic-api/workspace/";
            location.href = next.startsWith("/") ? next : "/deterministic-api/workspace/";
            done();
          } catch (err) {
            done(err);
          }
        },
        error_callback: (err) => {
          done(new Error(err?.message || err?.type || "Google sign-in failed"));
        },
      });
      tokenClient.requestAccessToken({ prompt: "select_account" });
    });
  }

  async function bootSignin() {
    const status = $("#status");
    const err = new URLSearchParams(location.search).get("error");
    if (err) setStatus(status, `Sign-in failed (${err})`, "is-error");

    const { data: cfg } = await api("/v1/customer-auth/public-config");

    function setTab(name) {
      document.querySelectorAll(".dapi-tab").forEach((tab) => {
        const on = tab.getAttribute("data-tab") === name;
        tab.classList.toggle("is-active", on);
        tab.setAttribute("aria-selected", on ? "true" : "false");
      });
      document.querySelectorAll(".dapi-panel-auth").forEach((panel) => {
        const on = panel.id === `panel-${name}`;
        panel.classList.toggle("is-active", on);
        panel.hidden = !on;
      });
      const title = $("#gate-title");
      const lede = document.querySelector(".dapi-gate__lede");
      if (title) title.textContent = name === "signin" ? "Sign in" : "Welcome";
      if (lede) {
        lede.textContent =
          name === "signin"
            ? "Continue with GitHub or Google."
            : "$10 trial. Keys stay in the workspace.";
      }
    }

    document.querySelectorAll(".dapi-tab").forEach((tab) => {
      tab.addEventListener("click", () => setTab(tab.getAttribute("data-tab") || "start"));
    });

    // Deep-link: returning users land on Sign in
    if (new URLSearchParams(location.search).get("mode") === "signin") setTab("signin");

    $("#register-form")?.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      setStatus(status, "Creating workspace…");
      const { res, data } = await api("/v1/customer-auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: String(fd.get("email") || ""),
          caller_site: "www.noetfield.com/deterministic-api/signin",
        }),
      });
      if (!res.ok || !data.ok || !data.session_token) {
        setStatus(
          status,
          errMsg(data, "Could not start. If you already have an account, use Sign in."),
          "is-error",
        );
        return;
      }
      setSession(data.session_token);
      const next = new URLSearchParams(location.search).get("next") || "/deterministic-api/workspace/";
      location.href = next.startsWith("/") ? next : "/deterministic-api/workspace/";
    });

    $("#btn-google")?.addEventListener("click", async () => {
      try {
        await signInWithGoogle(cfg, status);
      } catch (e) {
        setStatus(status, e.message || String(e), "is-error");
      }
    });
    $("#btn-github")?.addEventListener("click", () => {
      if (!cfg.providers?.github) {
        setStatus(status, "GitHub sign-in is not configured on the API yet.", "is-error");
        return;
      }
      const next = encodeURIComponent(
        new URLSearchParams(location.search).get("next") ||
          "https://www.noetfield.com/deterministic-api/workspace/",
      );
      location.href = `${API}/v1/customer-auth/github/start?next=${next}`;
    });
    $("#key-form")?.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      setStatus(status, "Unlocking…");
      const { res, data } = await api("/v1/customer-auth/api-key", {
        method: "POST",
        body: JSON.stringify({ api_key: String(fd.get("api_key") || "") }),
      });
      if (!res.ok || !data.ok || !data.session_token) {
        setStatus(status, errMsg(data, "Unlock failed"), "is-error");
        return;
      }
      setSession(data.session_token);
      location.href = "/deterministic-api/workspace/";
    });
  }

  async function bootWorkspace() {
    absorbHashSession();
    if (!getSession()) {
      const q = location.search || "";
      location.replace(`/deterministic-api/signin/?next=${encodeURIComponent("/deterministic-api/workspace/" + q)}`);
      return;
    }

    const banner = $("#topup-banner");
    if (banner && new URLSearchParams(location.search).get("topup") === "success") {
      banner.hidden = false;
    }

    const { res: meRes, data: me } = await api("/v1/customer/me");
    if (!meRes.ok || !me.authenticated) {
      setSession("");
      location.replace("/deterministic-api/signin/?next=/deterministic-api/workspace/");
      return;
    }
    const emailEl = $("#user-email");
    if (emailEl) emailEl.textContent = me.user?.email || "";
    const live = $("#live-chip");
    if (live) live.hidden = false;

    $("#signout-btn")?.addEventListener("click", async () => {
      await api("/v1/customer/signout", { method: "POST", body: "{}" });
      setSession("");
      location.href = "/deterministic-api/";
    });

    const status = $("#topup-status");
    const { res, data } = await api("/v1/customer/workspace");
    if (!res.ok || !data.ok) {
      setStatus(status, errMsg(data, "Could not load workspace"), "is-error");
      return;
    }
    const ws = data.workspace || {};
    const bal = $("#api-balance");
    if (bal) bal.textContent = `$${(typeof ws.balance_usd === "number" ? ws.balance_usd : 0).toFixed(2)}`;
    const tenant = $("#api-tenant");
    if (tenant) tenant.textContent = ws.tenant_id ? `tenant ${ws.tenant_id}` : "";

    const keysEl = $("#api-keys");
    const keyCount = $("#key-count");
    function renderKeys(keys) {
      const list = keys || [];
      if (keyCount) keyCount.textContent = `${list.length} active`;
      if (!keysEl) return;
      keysEl.innerHTML = list.length
        ? list
            .map(
              (k) =>
                `<div class="dapi-key-row"><code>${escapeHtml(k.key_hash_prefix)}…</code> <span class="dapi-pill">${escapeHtml(k.status || "active")}</span></div>`,
            )
            .join("")
        : '<p class="dapi-muted">No keys yet. Generate one below — only while signed in.</p>';
    }
    renderKeys(ws.keys || []);

    const planKicker = $("#plan-kicker");
    const planStatus = $("#plan-status");
    const codingSnippet = $("#coding-pro-snippet");
    const dropIn = $("#drop-in-code");

    function renderPlan(planId, workspace) {
      const id = planId || (workspace && workspace.product_plan) || "standard";
      if (planKicker) planKicker.textContent = id === "coding_pro" ? "coding_pro" : "standard";
      if (codingSnippet) codingSnippet.hidden = id !== "coding_pro";
      if (dropIn) {
        const model = id === "coding_pro" ? "noetfield-coding-pro" : "noetfield-deterministic";
        dropIn.textContent =
          'base_url = "https://nf-deterministic-api-v1.sina-kazemnezhad-ca.workers.dev/v1"\n' +
          'api_key  = "sk-nf-…"\n' +
          `model    = "${model}"`;
      }
    }
    renderPlan(ws.product_plan, ws);

    async function setPlan(product_plan) {
      setStatus(planStatus, product_plan === "coding_pro" ? "Enabling Coding Pro…" : "Switching to Standard…");
      const { res: pRes, data: pData } = await api("/v1/customer/plan", {
        method: "POST",
        body: JSON.stringify({ product_plan }),
      });
      if (!pRes.ok || !pData.ok) {
        setStatus(planStatus, errMsg(pData, "Could not update plan"), "is-error");
        return;
      }
      renderPlan(pData.product_plan, null);
      setStatus(
        planStatus,
        pData.product_plan === "coding_pro"
          ? "Coding Pro on — use model noetfield-coding-pro (~4× token rate)."
          : "Standard lane active — model noetfield-deterministic.",
        "is-ok",
      );
    }

    $("#enable-coding-pro-btn")?.addEventListener("click", () => setPlan("coding_pro"));
    $("#use-standard-btn")?.addEventListener("click", () => setPlan("standard"));

    const newKey = $("#api-newkey");
    const newKeyTools = $("#api-newkey-tools");
    const keyStatus = $("#key-status");
    const genBtn = $("#generate-key-btn");

    $("#copy-key-btn")?.addEventListener("click", async () => {
      const ok = await copyText(lastRawKey);
      setStatus(keyStatus, ok ? "Key copied to clipboard." : "Could not copy — select the key manually.", ok ? "is-ok" : "is-error");
    });

    $("#copy-dropin-btn")?.addEventListener("click", async () => {
      const code = ($("#drop-in-code")?.textContent || "").trim();
      const ok = await copyText(code);
      setStatus(status, ok ? "Snippet copied." : "Could not copy snippet.", ok ? "is-ok" : "is-error");
    });

    genBtn?.addEventListener("click", async () => {
      genBtn.disabled = true;
      setStatus(keyStatus, "Generating API key…");
      const { res: kRes, data: kData } = await api("/v1/customer/keys", {
        method: "POST",
        body: "{}",
      });
      genBtn.disabled = false;
      if (!kRes.ok || !kData.ok || !kData.api_key) {
        setStatus(keyStatus, errMsg(kData, "Could not generate API key"), "is-error");
        return;
      }
      lastRawKey = kData.api_key;
      setStatus(keyStatus, "Key created — copy it now. It will not be shown again.", "is-ok");
      if (newKey) {
        newKey.hidden = false;
        newKey.textContent = `New API key (copy now):\n${kData.api_key}`;
      }
      if (newKeyTools) newKeyTools.hidden = false;
      const { res: wRes, data: wData } = await api("/v1/customer/workspace");
      if (wRes.ok && wData.ok) renderKeys((wData.workspace || {}).keys || []);
    });

    $("#topup-btn")?.addEventListener("click", async () => {
      setStatus(status, "Opening Stripe Checkout…");
      const { res: cRes, data: cData } = await api("/v1/customer/checkout", {
        method: "POST",
        body: JSON.stringify({ amount_cents: 1000 }),
      });
      if (!cRes.ok || !cData.ok || !cData.checkout_url) {
        setStatus(status, errMsg(cData, "Checkout failed"), "is-error");
        return;
      }
      location.href = cData.checkout_url;
    });
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  window.NFDapi = { bootSignin, bootWorkspace };
})();
