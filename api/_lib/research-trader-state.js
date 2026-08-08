/**
 * Normalize and validate the ai-trader public cycle feed.
 *
 * Fail closed. The page this feeds argues that its numbers are checkable, so a
 * figure that cannot be dated must never reach it: six real counts with no
 * timestamp are worse than showing nothing, because the reader has no way to
 * know they are current. Every rejection below is a case where the honest
 * answer is "not available" rather than a number.
 */

const CYCLE_SCHEMA_PREFIX = "noetfield.ai-trader-research-cycle.";

/** A day, plus room for GitHub Actions cron drift and a daylight-saving shift. */
const CURRENT_MAX_AGE_S = 26 * 3600;
const LATE_MAX_AGE_S = 72 * 3600;

/** Clock skew we tolerate on an upstream timestamp before calling it broken. */
const FUTURE_TOLERANCE_MS = 15 * 60 * 1000;

function count(value) {
  const n = Number(value);
  return Number.isInteger(n) && n >= 0 ? n : null;
}

function money(value) {
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

function text(value) {
  return typeof value === "string" && value ? value : null;
}

function instant(value, nowMs) {
  if (typeof value !== "string" || !value) return null;
  const t = Date.parse(value);
  if (!Number.isFinite(t)) return null;
  // A timestamp in the future means a broken clock upstream, not fresh data.
  if (t > nowMs + FUTURE_TOLERANCE_MS) return null;
  return { iso: value, ms: t };
}

function classify(ageSeconds) {
  if (ageSeconds === null || ageSeconds === undefined) return "unknown";
  if (ageSeconds <= CURRENT_MAX_AGE_S) return "current";
  if (ageSeconds <= LATE_MAX_AGE_S) return "late";
  return "stale";
}

/**
 * Returns a fully-formed payload or { available: false, reason }.
 * Never returns a partial: a half-validated payload is the failure this exists
 * to prevent.
 */
function normalize(raw, nowMs) {
  if (!raw || typeof raw !== "object") {
    return { available: false, reason: "upstream_malformed" };
  }
  if (raw.storeAvailable !== true) {
    return { available: false, reason: "store_unavailable" };
  }

  const latest = raw.latest;
  if (!latest || typeof latest !== "object") {
    return { available: false, reason: "store_unavailable" };
  }
  if (typeof latest.schema !== "string" || latest.schema.indexOf(CYCLE_SCHEMA_PREFIX) !== 0) {
    return { available: false, reason: "upstream_malformed" };
  }

  // No completion time means no figure on this page can be dated, so none of
  // them may be shown. This is the load-bearing check.
  const completed = instant(latest.completedAtIso, nowMs);
  if (!completed) {
    return { available: false, reason: "upstream_malformed" };
  }

  const stats = raw.stats && typeof raw.stats === "object" ? raw.stats : {};
  const totals = {
    cyclesRun: count(stats.cyclesRun),
    screenings: count(stats.symbolsScreened),
    // Deliberately not "plansWritten": the upstream counter includes cycles
    // where the model declined outright, so calling these "plans" would
    // overstate what the gate has actually refused.
    modelVerdicts: count(stats.plansWritten),
    clearedGate: count(stats.plansPassed),
    spendUsd: money(raw.totalSpendUsd),
  };

  const required = ["cyclesRun", "screenings", "modelVerdicts", "clearedGate", "spendUsd"];
  for (let i = 0; i < required.length; i += 1) {
    if (totals[required[i]] === null) {
      return { available: false, reason: "upstream_malformed" };
    }
  }

  // Internally inconsistent counts are malformed, not renderable.
  if (totals.clearedGate > totals.modelVerdicts) {
    return { available: false, reason: "upstream_malformed" };
  }
  if (totals.cyclesRun > 0 && totals.screenings < totals.cyclesRun) {
    return { available: false, reason: "upstream_malformed" };
  }

  // Publish a rate only when the feed and the counts agree on it.
  const reported = Number(stats.gatePassPct);
  const derived = totals.modelVerdicts > 0
    ? (totals.clearedGate / totals.modelVerdicts) * 100
    : null;
  totals.gatePassPct =
    derived !== null && Number.isFinite(reported) && Math.round(reported) === Math.round(derived)
      ? reported
      : null;

  const started = instant(latest.startedAtIso, nowMs);
  const cost = latest.cost && typeof latest.cost === "object" ? latest.cost : {};
  const ageSeconds = Math.round((nowMs - completed.ms) / 1000);

  return {
    available: true,
    cycle: {
      proofRunId: text(latest.proofRunId),
      state: text(latest.state),
      mode: text(latest.mode),
      startedAtIso: started ? started.iso : null,
      completedAtIso: completed.iso,
      watchlistCount: Array.isArray(latest.watchlist) ? latest.watchlist.length : null,
      symbolsScreened: count(latest.screenedCount),
      costUsd: money(cost.totalUsd),
      costBasis: text(cost.basis),
    },
    totals,
    freshness: {
      ageSeconds: ageSeconds,
      class: classify(ageSeconds),
      computedFrom: "completedAtIso",
    },
    note: text(typeof raw.error === "string" ? raw.error.trim() : null),
  };
}

module.exports = { normalize, classify, CURRENT_MAX_AGE_S, LATE_MAX_AGE_S };
