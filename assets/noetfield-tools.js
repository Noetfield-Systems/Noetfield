(function () {
  var LOAD = 1.3;
  var WEEKS = 48;
  var HOBBY = 3000;
  var NOTICE = "Nothing is posted. Nothing is stored.";

  function money(n) {
    var v = Number.isFinite(n) && n > 0 ? n : 0;
    return new Intl.NumberFormat("en-CA", {
      style: "currency",
      currency: "CAD",
      maximumFractionDigits: 0,
    }).format(Math.round(v));
  }

  function hours(n) {
    var v = Number.isFinite(n) && n > 0 ? n : 0;
    return (Math.round(v * 10) / 10).toString();
  }

  function num(form, name) {
    return Number(form.elements[name] && form.elements[name].value ? form.elements[name].value : 0);
  }

  function sel(form, name) {
    var el = form.elements[name];
    return el ? String(el.value || "") : "";
  }

  function checked(form, name) {
    var el = form.elements[name];
    return !!(el && el.checked);
  }

  function processCost(touches, minutes, rate, people) {
    return Number(touches) * (Number(minutes) / 60) * Number(rate) * LOAD * Number(people) * WEEKS;
  }

  function pack(kind, amount, headline, body, extra, cta, math, action) {
    var memo = [
      amount,
      headline,
      body,
      math ? "Math: " + math : "",
      action ? "Next: " + action : "",
      NOTICE,
    ]
      .filter(Boolean)
      .join("\n");
    return {
      kind: kind,
      amount: amount,
      headline: headline,
      body: body,
      extra: extra || "",
      cta: cta,
      math: math || "",
      action: action || "",
      memo: memo,
    };
  }

  var CTAS = {
    app: { href: "https://app.noetfield.com/", label: "Open the app" },
    readiness: { href: "https://www.noetfield.com/copilot/pilot/", label: "Copilot pilot" },
    brief: { href: "https://www.noetfield.com/trust-brief/", label: "Trust Brief" },
    intake: { href: "https://www.noetfield.com/trust-brief/intake/", label: "Trust Brief intake" },
    calculator: { href: "https://sourcea.app/calculator", label: "Full process-cost calculator" },
    tools: { href: "/tools/", label: "See the other checks" },
  };

  function compute(tool, form) {
    if (tool === "quiet-leak") {
      var touches = num(form, "touches");
      var minutes = num(form, "minutes");
      var rate = num(form, "rate");
      var people = num(form, "people");
      var cost = processCost(touches, minutes, rate, people);
      var weekHours = touches * (minutes / 60) * people;
      var math =
        touches +
        " touches/week × " +
        minutes +
        " min × " +
        money(rate) +
        "/hr × 1.3 load × " +
        people +
        " people × 48 weeks = " +
        money(cost) +
        " (" +
        hours(weekHours) +
        " hours/week)";
      if (cost < HOBBY) {
        return pack(
          "leave",
          money(cost) + " / year",
          "Leave it alone.",
          "Under $3,000 a year, automating this is a hobby, not an investment. The page says that out loud instead of selling you a fix.",
          "Count one real day before you trust the estimate. People undercount touches by about half.",
          "calculator",
          math,
          "Count one real day. If it stays under $3,000, stop."
        );
      }
      if (cost < 15000) {
        return pack(
          "look",
          money(cost) + " / year",
          "Real money. Still not a platform.",
          "Price one leak first. If the number is real, start with one named goal and a check that can fail.",
          hours(weekHours) + " hours a week across the people who do this.",
          "app",
          math,
          "Write the two system names and the owner on one line. That is the goal."
        );
      }
      return pack(
        "act",
        money(cost) + " / year",
        "This leak is large enough to name.",
        "Give this process as a goal in the open alpha. Plan, run, check, stop for your decision. Founder-operated. No fake customer logos.",
        hours(weekHours) + " hours a week. That is labor, not a software feature request.",
        "app",
        math,
        "Name the leak as one goal. Do not start a suite."
      );
    }

    if (tool === "ai-spend") {
      var monthly = Math.max(0, num(form, "monthly"));
      var attributedPct = Math.min(100, Math.max(0, num(form, "attributed")));
      var share = attributedPct / 100;
      var teams = Math.max(1, num(form, "teams") || 1);
      var named = sel(form, "named") === "yes";
      var unexplainedMonthly = monthly * (1 - share);
      var annual = unexplainedMonthly * 12;
      var amount = money(annual) + " / year unattributed";
      var math =
        money(monthly) +
        "/mo × " +
        (100 - attributedPct) +
        "% unexplained × 12 = " +
        money(annual) +
        ". Teams: " +
        teams +
        ". Named accepter: " +
        (named ? "yes" : "no") +
        ".";
      if (monthly < 1500 && teams <= 1) {
        return pack(
          "leave",
          amount,
          "Leave it alone.",
          "Under about $1,500 a month and one team, a spreadsheet is enough. Do not buy a governance stack for a hobby.",
          "",
          "tools",
          math,
          "Keep a one-line sheet: invoice, owner, workflow. Stop shopping."
        );
      }
      if (named && share >= 0.2) {
        return pack(
          "leave",
          amount,
          "You already have the bones.",
          "Named workflow and named accepter. Do not buy a platform tour. Tighten the receipt, then stop shopping.",
          "",
          "app",
          math,
          "Write the workflow name and the accepter next to last month’s invoice. Done."
        );
      }
      if (share < 0.2) {
        return pack(
          "act",
          amount,
          "The leak is explanation, not tokens.",
          "Under 20% attributed, nobody can defend the bill. Name one workflow, one owner, and who accepts output before it leaves.",
          "People count licensed Copilot and forget personal ChatGPT. That unofficial line is often larger.",
          "readiness",
          math,
          "Pick one workflow. Attribute its share of the invoice. Name who accepts output."
        );
      }
      return pack(
        "look",
        amount,
        "Attribute more before you buy more.",
        "Spend is large enough to care. The next honest step is a named workflow and a named accepter, not another seat.",
        "",
        "app",
        math,
        "Do not add seats until a named workflow owns 20% of the bill."
      );
    }

    if (tool === "who-accepted") {
      var deliverables = Math.max(0, num(form, "deliverables"));
      var signedPct = Math.min(100, Math.max(0, num(form, "signed")));
      var signed = signedPct / 100;
      var minutes = Math.max(0, num(form, "minutes"));
      var rate = Math.max(0, num(form, "rate"));
      var replay = sel(form, "replay") === "yes";
      var unsignedWeek = deliverables * (1 - signed);
      var redo = unsignedWeek * (minutes / 60) * rate * LOAD * WEEKS;
      var unsignedYear = unsignedWeek * WEEKS;
      var amount = money(redo) + " / year of unsigned redo";
      var math =
        hours(unsignedWeek) +
        " unsigned items/week × " +
        minutes +
        " min redo × " +
        money(rate) +
        "/hr × 1.3 × 48 weeks = " +
        money(redo) +
        ". Named signer: " +
        signedPct +
        "%. Replayable why: " +
        (replay ? "yes" : "no") +
        ".";
      if (signed >= 0.9 && replay) {
        return pack(
          "leave",
          amount,
          "Leave it alone.",
          "A named signer and a replayable why. You do not need another copilot. Keep the receipt. Stop shopping.",
          "",
          "tools",
          math,
          "Keep the reason next to the signature. Do not buy another tool."
        );
      }
      if (signed < 0.5 || !replay) {
        return pack(
          "act",
          amount,
          "That is a chat log, not a process.",
          "Name who accepts, keep the reason, and let a check fail. One real goal in the open alpha is enough to try that.",
          Math.round(unsignedYear) + " unsigned outputs a year. The builder must not grade itself.",
          "app",
          math,
          "Name the accepter for last week’s last draft. If you cannot, start one goal in the app."
        );
      }
      return pack(
        "look",
        amount,
        "Close the replay gap.",
        "Signing without a why still fails a board question. Record the pass/fail reason before you buy more seats.",
        "",
        "app",
        math,
        "Add one sentence of why to the next signed output. That is the receipt."
      );
    }

    if (tool === "copilot-seats") {
      var licensed = Math.max(0, num(form, "licensed"));
      var usedRaw = Math.max(0, num(form, "used"));
      var used = Math.min(licensed, usedRaw);
      var clipped = usedRaw > licensed;
      var hoursPer = Math.max(0, num(form, "hours"));
      var wage = Math.max(0, num(form, "rate"));
      var seat = Math.max(0, num(form, "seat"));
      var unused = Math.max(0, licensed - used);
      var waste = unused * seat;
      var ungoverned = used * hoursPer * wage * LOAD * WEEKS;
      var amount = money(waste) + " unused licenses · " + money(ungoverned) + " ungoverned use / year";
      var math =
        unused +
        " unused × " +
        money(seat) +
        "/seat = " +
        money(waste) +
        ". " +
        used +
        " used × " +
        hoursPer +
        " hrs/week × " +
        money(wage) +
        "/hr × 1.3 × 48 = " +
        money(ungoverned) +
        ".";
      var clipNote = clipped ? " Used seats were capped at licensed seats." : "";
      if (unused < 10 && licensed <= 20) {
        return pack(
          "leave",
          amount,
          "Fix adoption. Do not buy policy.",
          "Unused seats under about 10 is not a governance purchase. Turn unused licenses off, or train the people who have them.",
          "Showing only the unused-license number is how a post stays dishonest. The used-seat line is usually larger." + clipNote,
          "tools",
          math,
          "Turn off unused seats this week, or train the people who have them. Do not buy a control plane."
        );
      }
      if (used >= 10 && hoursPer >= 2) {
        return pack(
          "act",
          amount,
          "You are paying for labor with no trail.",
          "The used-seat line is the one that matters. Name the workflow, the owner, and who accepts output.",
          clipNote.trim(),
          "brief",
          math,
          "Take both numbers to finance. Ask who accepted last week’s Copilot output."
        );
      }
      return pack(
        "look",
        amount,
        "Show both numbers to finance.",
        "License waste is visible. Ungoverned use is usually larger and quieter. Do not let a seat-optimization slide hide the second number.",
        clipNote.trim(),
        "readiness",
        math,
        "Put unused-license waste and ungoverned-use cost on the same slide."
      );
    }

    if (tool === "board-five") {
      var qs = [
        ["workflow", "name the workflow"],
        ["owner", "name the owner"],
        ["spend", "name last month’s spend"],
        ["failed", "name the last failure"],
        ["accepted", "name who accepted the last output"],
      ];
      var yes = [];
      var no = [];
      qs.forEach(function (row) {
        if (checked(form, row[0])) yes.push(row[1]);
        else no.push(row[1]);
      });
      var n = yes.length;
      var missing = no.length ? "Still no: " + no.join("; ") + "." : "All five named.";
      var math = n + " yes / 5. " + missing;
      if (n <= 1) {
        return pack(
          "leave",
          n + " / 5",
          "Do not buy.",
          "You are not ready for a diagnostic. Name the workflow and the owner first. Open the app if you want one real goal with a check that can fail.",
          missing,
          "app",
          math,
          "Answer the first two out loud in the next standup. Then stop shopping."
        );
      }
      if (n <= 3) {
        return pack(
          "look",
          n + " / 5",
          "Procurement may need a file. You do not need a tour.",
          "Copilot Readiness is the pack that can be filed. The missing yeses are still the work.",
          missing,
          "readiness",
          math,
          "Close the missing yeses before you buy a memo."
        );
      }
      return pack(
        "act",
        n + " / 5",
        "Trust Brief only if you need a board memo.",
        "You can already answer the room. Buy a memo if the board needs paper. Do not buy another copilot to feel busy.",
        missing,
        "intake",
        math,
        "If the board needs paper, use Trust Brief. If they need a process, open the app."
      );
    }

    return null;
  }

  function applyPreset(form, raw) {
    var data;
    try {
      data = JSON.parse(raw);
    } catch {
      return;
    }
    Object.keys(data).forEach(function (key) {
      var el = form.elements[key];
      if (!el) return;
      if (el.type === "checkbox") el.checked = !!data[key];
      else el.value = data[key];
    });
    if (Object.keys(data).length === 0) {
      Array.prototype.forEach.call(form.elements, function (el) {
        if (el.type === "checkbox") el.checked = false;
      });
    }
  }

  function applyParams(form) {
    var params = new URLSearchParams(window.location.search);
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || !params.has(el.name)) return;
      if (el.type === "checkbox") el.checked = params.get(el.name) === "1" || params.get(el.name) === "true";
      else el.value = params.get(el.name);
    });
  }

  function shareUrl(form) {
    var url = new URL(window.location.href);
    url.searchParams.delete("embed");
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name) return;
      if (el.type === "checkbox") url.searchParams.set(el.name, el.checked ? "1" : "0");
      else url.searchParams.set(el.name, String(el.value || ""));
    });
    return url.toString();
  }

  function flash(btn, text) {
    if (!btn) return;
    var prior = btn.textContent;
    btn.textContent = text;
    setTimeout(function () {
      btn.textContent = prior;
    }, 1600);
  }

  function setText(sel, value, hideIfEmpty) {
    var el = document.querySelector(sel);
    if (!el) return;
    el.textContent = value || "";
    if (hideIfEmpty) el.hidden = !value;
  }

  function render(tool, form) {
    var result = compute(tool, form);
    if (!result) return;
    var box = document.getElementById("nf-tools-result");
    var amount = document.querySelector("[data-result-amount]");
    var cta = document.querySelector("[data-result-cta]");
    if (box) box.setAttribute("data-kind", result.kind);
    if (amount) {
      amount.hidden = false;
      amount.textContent = result.amount;
    }
    setText("[data-result-headline]", result.headline);
    setText("[data-result-body]", result.body);
    setText("[data-result-extra]", result.extra, true);
    setText("[data-result-math]", result.math, true);
    setText("[data-result-action]", result.action, true);
    var dest = CTAS[result.cta] || CTAS.tools;
    if (cta) {
      cta.setAttribute("href", dest.href);
      cta.textContent = dest.label;
    }
    var memoEl = document.querySelector("[data-result-memo]");
    if (memoEl) memoEl.value = result.memo + "\n" + shareUrl(form);
  }

  function bootEmbedBlocks() {
    document.querySelectorAll("[data-embed-src]").forEach(function (block) {
      var src = block.getAttribute("data-embed-src");
      var code =
        '<iframe src="' +
        src +
        '" title="Noetfield tool" width="100%" height="820" style="border:0;border-radius:12px" loading="lazy"></iframe>';
      var slot = block.querySelector("code");
      if (slot) slot.textContent = code;
      var btn = block.querySelector("[data-copy-embed]");
      if (btn) {
        btn.addEventListener("click", function () {
          navigator.clipboard.writeText(code).then(function () {
            flash(btn, "Copied");
          }).catch(function () {
            window.prompt("Copy this embed", code);
          });
        });
      }
    });
  }

  function boot() {
    var params = new URLSearchParams(window.location.search);
    if (params.get("embed") === "1") document.body.classList.add("nf-tools--embed");
    bootEmbedBlocks();
    var tool = document.body.getAttribute("data-tool") || "";
    var form = document.getElementById("nf-tools-form");
    if (!form) return;
    applyParams(form);
    render(tool, form);
    form.addEventListener("input", function () {
      render(tool, form);
    });
    form.addEventListener("change", function () {
      render(tool, form);
    });
    form.addEventListener("submit", function (event) {
      event.preventDefault();
    });
    document.querySelectorAll("[data-preset]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyPreset(form, btn.getAttribute("data-preset") || "{}");
        render(tool, form);
      });
    });
    var share = document.getElementById("nf-tools-share");
    if (share) {
      share.addEventListener("click", function () {
        var href = shareUrl(form);
        navigator.clipboard.writeText(href).then(function () {
          flash(share, "Link copied");
        }).catch(function () {
          window.prompt("Copy this link", href);
        });
      });
    }
    var copy = document.getElementById("nf-tools-copy");
    if (copy) {
      copy.addEventListener("click", function () {
        var memoEl = document.querySelector("[data-result-memo]");
        var text = (memoEl && memoEl.value) || NOTICE;
        navigator.clipboard.writeText(text).then(function () {
          flash(copy, "Memo copied");
        });
      });
    }
  }

  window.NF_TOOLS_MATH = { LOAD: LOAD, WEEKS: WEEKS, money: money, processCost: processCost, compute: compute };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
