/* Noetfield Onchain Season 0 — LIVE POSTGRES XP + EIP-191 SIGNED WALLET.
   No browser-only balances, synthetic token claims, private keys or token transfers. */
(function () {
  "use strict";
  const API = "https://platform.noetfield.com/api/v1/onchain";
  const KEY = "noetfield_onchain_wallet_session_v1";
  const STORAGE = window.sessionStorage;
  const $ = (id) => document.getElementById(id);
  let provider = null, address = "", session = "", member = null, apiReady = false, pending = false;
  const code = new URLSearchParams(location.search).get("ref");
  const ref = /^[a-f0-9]{20}$/.test(code || "") ? code : null;
  let toastTimer;

  const truncate = (value) => value && value.length > 13 ? value.slice(0, 7) + "…" + value.slice(-5) : value;
  function showToast(message, isError) {
    const el = $("toast");
    if (!el) return;
    el.textContent = message; el.classList.toggle("error", Boolean(isError)); el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.hidden = true; }, 5800);
  }
  function status(target, text, isError) {
    const el = $(target); if (!el) return;
    el.textContent = text;
    el.classList.toggle("error", Boolean(isError));
  }
  async function request(path, options = {}, authenticated = false) {
    const headers = { Accept: "application/json", ...(options.body ? { "Content-Type": "application/json" } : {}) };
    if (authenticated) {
      if (!session) throw Error("Connect your wallet and sign in to continue.");
      headers.Authorization = "Bearer " + session;
    }
    const response = await fetch(API + path, { ...options, headers, cache: "no-store", mode: "cors" });
    let body = {};
    try { body = await response.json(); } catch (_) { /* response may be error page */ }
    if (!response.ok) {
      if (response.status === 401 && authenticated) {
        session = ""; member = null; STORAGE.removeItem(KEY); render();
      }
      const detail = typeof body.detail === "string" ? body.detail : "The community service is temporarily unavailable.";
      throw Error(detail);
    }
    return body;
  }
  function post(path, body, authenticated = false) {
    return request(path, { method: "POST", body: JSON.stringify(body) }, authenticated);
  }
  function availableProviders() {
    const all = [];
    if (Array.isArray(window.ethereum?.providers)) all.push(...window.ethereum.providers);
    else if (window.ethereum) all.push(window.ethereum);
    return Array.from(new Set(all));
  }
  // EIP-6963 multi-wallet discovery for modern injected EVM wallets.
  const announced = [];
  window.addEventListener("eip6963:announceProvider", (event) => {
    const detail = event.detail;
    if (detail && detail.provider && !announced.some((x) => x.provider === detail.provider)) announced.push(detail);
  });
  window.dispatchEvent(new Event("eip6963:requestProvider"));
  function chooseProvider() {
    if (provider) return provider;
    const eip = announced.map((p) => p.provider);
    const all = Array.from(new Set([...eip, ...availableProviders()]));
    if (!all.length) {
      throw Error("No EVM wallet detected. Open this page inside MetaMask, Coinbase Wallet, Rabby or another EVM wallet browser.");
    }
    // Prefer first provider announced by user-installed wallet; no hidden wallet selection or custody.
    provider = all[0];
    return provider;
  }
  async function ensureBase(p) {
    const id = await p.request({ method: "eth_chainId" });
    if (String(id).toLowerCase() === "0x2105") return; // Base mainnet: 8453
    try {
      await p.request({ method: "wallet_switchEthereumChain", params: [{ chainId: "0x2105" }] });
    } catch (err) {
      if (err && err.code === 4902) {
        await p.request({ method: "wallet_addEthereumChain", params: [{
          chainId: "0x2105", chainName: "Base",
          nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
          rpcUrls: ["https://mainnet.base.org"],
          blockExplorerUrls: ["https://basescan.org"]
        }] });
        return;
      }
      throw Error("Switch your wallet to Base to join the Noetfield network.");
    }
  }
  function hexMessage(message) {
    return "0x" + Array.from(new TextEncoder().encode(message), (b) => b.toString(16).padStart(2, "0")).join("");
  }
  async function connectWallet() {
    if (pending) return;
    pending = true;
    try {
      if (!apiReady) throw Error("Community API is unavailable. No account or points were created.");
      const p = chooseProvider();
      const accounts = await p.request({ method: "eth_requestAccounts" });
      if (!Array.isArray(accounts) || !accounts[0] || !/^0x[0-9a-f]{40}$/i.test(accounts[0])) {
        throw Error("Wallet did not return a valid EVM account.");
      }
      await ensureBase(p);
      address = accounts[0].toLowerCase();
      const challenge = await post("/challenge", { wallet: address });
      if (!challenge.message || !challenge.nonce) throw Error("Signature challenge was unavailable.");
      showToast("Confirm the sign-in request in your wallet. No gas or payment required.");
      const signature = await p.request({ method: "personal_sign", params: [hexMessage(challenge.message), accounts[0]] });
      if (!/^0x[0-9a-f]+$/i.test(signature) || signature.length < 130) throw Error("Wallet did not provide a signature.");
      const result = await post("/verify", { wallet: address, nonce: challenge.nonce, signature, ref });
      if (!result.session || !result.member) throw Error("Signed wallet session could not be established.");
      session = result.session; member = result.member;
      STORAGE.setItem(KEY, session);
      render();
      showToast("Wallet verified. Your participation passport is ready.");
      await loadLeaderboard();
    } catch (e) {
      showToast(e instanceof Error ? e.message : "Wallet sign-in failed.", true);
    } finally { pending = false; render(); }
  }
  function render() {
    const connected = Boolean(member && session);
    $("walletAddress").textContent = connected ? truncate(member.wallet) : "Connect an EVM wallet";
    $("walletSubline").textContent = connected ? "Verified wallet · Base network" : "Sign once. No funds leave your wallet.";
    $("walletState").textContent = connected ? "VERIFIED" : "NOT CONNECTED";
    $("xp").textContent = connected ? Number(member.xp).toLocaleString("en-CA") : "—";
    $("streak").textContent = connected ? member.streak : "—";
    $("claimStatus").textContent = connected ? member.claim_available ? "READY" : "DONE" : "—";
    $("claimHint").textContent = connected ? member.claim_available ? "Available now" : "Resets 00:00 UTC" : "After sign-in";
    $("connectWallet").textContent = connected ? "Verified passport · " + truncate(member.wallet) : "Connect & sign your passport ↗";
    $("connectWallet").disabled = connected || pending || !apiReady;
    $("connectNav").textContent = connected ? truncate(member.wallet) : "Connect wallet ↗";
    $("connectHero").textContent = connected ? "Open your daily quest ↗" : "Connect wallet & join ↗";
    $("connectBottom").textContent = connected ? "View your daily quest ↗" : "Connect wallet & join ↗";
    $("dailyClaim").disabled = !connected || !member.claim_available || pending;
    $("dailyClaim").textContent = !connected ? "Connect wallet to claim" : member.claim_available ? "Claim today's XP ↗" : "Today's XP claimed ✓";
    $("inviteLink").value = connected ? member.referral_url || "" : "";
    $("copyInvite").disabled = !connected;
    $("shareInvite").disabled = !connected;
    $("joinRegistry").disabled = !connected || pending;
    $("joinRegistry").textContent = connected ? "Join the founding registry ↗" : "Connect wallet to join";
    $("leaderboardOptIn").disabled = !connected;
    $("leaderboardOptIn").checked = connected && Boolean(member.leaderboard_opt_in);
  }
  async function checkBackend() {
    try {
      const s = await request("/status");
      apiReady = Boolean(s.database_ready && s.daily_quest?.status === "active");
      status("backendState", apiReady ? "NETWORK ONLINE · DAILY XP ACTIVE" : "NETWORK TEMPORARILY UNAVAILABLE", !apiReady);
      if (s.token?.issued && s.token?.contract) {
        $("tokenContract").textContent = truncate(s.token.contract);
      }
      if (!apiReady) showToast("Wallet program is temporarily unavailable. No claim is recorded until the service confirms it.", true);
    } catch (_) {
      apiReady = false;
      status("backendState", "NETWORK TEMPORARILY UNAVAILABLE", true);
    }
    render();
  }
  async function restoreSession() {
    try { session = STORAGE.getItem(KEY) || ""; } catch (_) { session = ""; }
    if (!session || !apiReady) return;
    try { member = await request("/me", {}, true); address = member.wallet; }
    catch (_) { session = ""; member = null; try { STORAGE.removeItem(KEY); } catch (_) {} }
    render();
  }
  async function claim() {
    if (!member || !member.claim_available || pending) return;
    pending = true; render();
    try {
      status("dailyStatus", "Recording today's claim...");
      const r = await post("/daily-claim", {}, true);
      member = r.member;
      render();
      status("dailyStatus", r.already_claimed ? "Already claimed today. Return after 00:00 UTC." : "+" + r.xp_awarded + " XP saved to your verified record.");
      showToast(r.already_claimed ? "Already claimed today" : "+" + r.xp_awarded + " XP claimed and stored");
      await loadLeaderboard();
    } catch (e) { status("dailyStatus", e.message, true); showToast(e.message, true); }
    finally { pending = false; render(); }
  }
  async function copyText(value) {
    if (!value) throw Error("Connect first to generate your invite link.");
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value); return;
    }
    const input = $("inviteLink");
    input.focus(); input.select();
    if (!document.execCommand("copy")) throw Error("Select the link to copy it manually.");
  }
  async function share() {
    if (!member) return;
    try {
      const url = member.referral_url;
      if (navigator.share) await navigator.share({
        title: "Noetfield Onchain network",
        text: "Join a real RWA + AI agent builder ecosystem. Connect a wallet, participate in daily quests and build the programmable economy.",
        url
      });
      else { await copyText(url); showToast("Referral link copied"); }
    } catch (e) { if (e.name !== "AbortError") showToast(e.message, true); }
  }
  async function loadLeaderboard() {
    const target = $("leaderboard");
    try {
      const r = await request("/leaderboard");
      target.replaceChildren();
      if (!Array.isArray(r.members) || r.members.length === 0) {
        target.textContent = "No members have opted in to the public leaderboard yet.";
        target.className = "board-list board-empty";
        return;
      }
      target.className = "board-list";
      for (const [index, m] of r.members.entries()) {
        const line = document.createElement("div"); line.className = "board-item";
        const name = document.createElement("span"); name.textContent = String(index + 1).padStart(2, "0") + " / " + m.wallet;
        const xp = document.createElement("b"); xp.textContent = Number(m.xp).toLocaleString() + " XP";
        line.append(name, xp); target.appendChild(line);
      }
    } catch (_) { target.textContent = "Leaderboard unavailable. No public scores were invented."; }
  }
  async function joinRegistry(event) {
    event.preventDefault();
    if (!session) return connectWallet();
    const interest = $("interest").value;
    const email = $("email").value.trim();
    const optIn = $("emailOptIn").checked;
    status("waitlistStatus", "Recording your interests...");
    try {
      const result = await post("/waitlist", { interest, email: email || null, email_opt_in: optIn }, true);
      if (result.joined) {
        status("waitlistStatus", "Your wallet-linked interest has been recorded." + (result.email_updates ? " Email updates enabled." : ""));
        showToast("Welcome to the founding interest registry");
      }
    } catch (e) { status("waitlistStatus", e.message, true); showToast(e.message, true); }
  }
  async function toggleLeaderboard() {
    if (!member) return;
    const selected = $("leaderboardOptIn").checked;
    try {
      await post("/preferences", { leaderboard_opt_in: selected }, true);
      member.leaderboard_opt_in = selected;
      await loadLeaderboard();
      showToast(selected ? "Public XP ranking enabled" : "Public XP ranking disabled");
    } catch (e) { $("leaderboardOptIn").checked = !selected; showToast(e.message, true); }
  }
  function entry() {
    if (member) { document.getElementById("quests").scrollIntoView({ behavior: "smooth" }); return; }
    return connectWallet();
  }
  function tokenUpdates() {
    $("interest").value = "token-updates";
    $("founding").scrollIntoView({ behavior: "smooth" });
    if (!member) showToast("Connect your wallet to record token updates interest.");
  }
  function mount() {
    for (const name of ["connectNav", "connectHero", "connectBottom"]) $(name)?.addEventListener("click", entry);
    $("connectWallet").addEventListener("click", connectWallet);
    $("dailyClaim").addEventListener("click", claim);
    $("copyInvite").addEventListener("click", async () => {
      try { await copyText(member?.referral_url); showToast("Your personal invite link is copied."); }
      catch (e) { showToast(e.message, true); }
    });
    $("shareInvite").addEventListener("click", share);
    $("tokenJoin").addEventListener("click", tokenUpdates);
    $("foundingForm").addEventListener("submit", joinRegistry);
    $("leaderboardOptIn").addEventListener("change", toggleLeaderboard);
    if (window.ethereum?.on) {
      window.ethereum.on("accountsChanged", () => {
        address = ""; session = ""; member = null; STORAGE.removeItem(KEY);
        render(); showToast("Wallet account changed. Sign again to protect your passport.");
      });
    }
    render();
    checkBackend().then(async () => {
      if (apiReady) { await restoreSession(); await loadLeaderboard(); }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount, { once: true });
  else mount();
})();
