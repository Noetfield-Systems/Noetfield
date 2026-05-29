/* Noetfield public assistant — calls backend only; never embed API keys */
(function () {
  "use strict";

  function apiBase() {
    var host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") return "http://127.0.0.1:8001";
    if (host.indexOf("platform.") === 0) return window.location.origin;
    return "https://platform.noetfield.com";
  }

  function sessionId() {
    var key = "nf_chat_sid";
    try {
      var existing = localStorage.getItem(key);
      if (existing) return existing;
      var sid = "c-" + Math.random().toString(36).slice(2, 12);
      localStorage.setItem(key, sid);
      return sid;
    } catch (_) {
      return "c-anon";
    }
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  function appendMsg(log, role, text) {
    var msg = el("div", "nfChatMsg " + role, text);
    log.appendChild(msg);
    log.scrollTop = log.scrollHeight;
  }

  function mount() {
    if (document.getElementById("nfChatFab")) return;

    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/assets/noetfield-chat.css";
    document.head.appendChild(link);

    var fab = el("button", "nfChatFab", "?");
    fab.id = "nfChatFab";
    fab.type = "button";
    fab.setAttribute("aria-label", "Open Noetfield assistant");

    var panel = el("div", "nfChatPanel");
    panel.id = "nfChatPanel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Noetfield assistant");

    var head = el("div", "nfChatHead");
    head.innerHTML =
      "<strong>Noetfield assistant</strong><span>Governance offerings &amp; intake (FAQ)</span>";

    var log = el("div", "nfChatLog");
    log.id = "nfChatLog";

    var note = el("div", "nfChatNote");
    note.textContent =
      "Answers use public site knowledge only. For contracts email operations@noetfield.com.";

    var form = el("form", "nfChatForm");
    var input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Ask about offerings, Trust Brief, Bank Pilot…";
    input.autocomplete = "off";
    input.maxLength = 2000;
    input.setAttribute("aria-label", "Your question");
    var send = el("button", "", "Send");
    send.type = "submit";
    form.appendChild(input);
    form.appendChild(send);

    panel.appendChild(head);
    panel.appendChild(log);
    panel.appendChild(note);
    panel.appendChild(form);
    document.body.appendChild(fab);
    document.body.appendChild(panel);

    appendMsg(
      log,
      "bot",
      "Hello. I can answer questions about Noetfield offerings, intake, and the Governance Console. How can I help?"
    );

    fab.addEventListener("click", function () {
      var open = panel.classList.toggle("open");
      fab.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) input.focus();
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var text = (input.value || "").trim();
      if (!text) return;
      input.value = "";
      appendMsg(log, "user", text);
      send.disabled = true;
      fetch(apiBase() + "/api/public/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId() }),
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          if (result.ok && result.data && result.data.reply) {
            appendMsg(log, "bot", result.data.reply);
            return;
          }
          var detail =
            (result.data && result.data.detail) ||
            "Assistant is unavailable. Use /trust-brief/intake/ or email operations@noetfield.com.";
          appendMsg(log, "bot", String(detail));
        })
        .catch(function () {
          appendMsg(
            log,
            "bot",
            "Could not reach the assistant service. Email operations@noetfield.com or visit /trust-brief/intake/."
          );
        })
        .finally(function () {
          send.disabled = false;
          input.focus();
        });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
