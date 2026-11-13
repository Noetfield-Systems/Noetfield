/* Noetfield Onchain / v7 – polish that preserves real intake, AI, wallet and demo routes. */
(function () {
  "use strict";
  const ready = (fn) => document.readyState === "loading"
    ? document.addEventListener("DOMContentLoaded", fn, { once: true })
    : fn();
  ready(function () {
    const page = document.querySelector(".v5-hero");
    const art = document.querySelector(".v5-campus");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const finePointer = window.matchMedia("(pointer: fine)");
    // Atmospheric movement is progressive only; UI controls do not move.
    if (page && art && !reduceMotion.matches && finePointer.matches) {
      let frame = 0, px = 0, py = 0;
      page.addEventListener("pointermove", (event) => {
        const box = page.getBoundingClientRect();
        px = (event.clientX - box.left) / box.width - .5;
        py = (event.clientY - box.top) / box.height - .5;
        if (frame) return;
        frame = window.requestAnimationFrame(() => {
          frame = 0;
          art.style.translate = (px * -8).toFixed(1) + "px " + (py * -4).toFixed(1) + "px";
        });
      }, { passive: true });
      page.addEventListener("pointerleave", () => { art.style.translate = "0 0"; }, { passive: true });
    }
    // Real commercial conversion: prefill existing project-intake from use cases.
    const caseSpecs = [
      { topic: "rwa-private-credit", note: "I'd like to scope a real-world asset tokenization/readiness workflow with an issuer operating model and integration plan." },
      { topic: "rwa-private-credit", note: "I'd like a scoped private-credit servicing, eligibility and policy-controlled execution workflow." },
      { topic: "stablecoin-operations", note: "I'd like an onchain treasury operations workflow with approval controls, provider integrations and reconciliation." }
    ];
    document.querySelectorAll(".v5-journey-grid > a").forEach((card, index) => {
      const spec = caseSpecs[index];
      if (!spec) return;
      card.addEventListener("click", function () {
        const form = document.getElementById("nfOnchainIntake");
        if (!form) return;
        const topic = form.querySelector('[name="topic"]');
        if (topic && topic.querySelector('option[value="' + spec.topic + '"]')) topic.value = spec.topic;
        const notes = form.querySelector('[name="notes"]');
        if (notes && (!notes.value.trim() || notes.value === notes.dataset.onchainAutofill)) {
          notes.value = spec.note;
          notes.dataset.onchainAutofill = spec.note;
        }
      });
    });
    const nav = document.getElementById("onchainNav");
    if (nav && "IntersectionObserver" in window) {
      const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
      const anchorMap = new Map(links.map(link => [link.getAttribute("href").slice(1), link]));
      const sections = [...anchorMap.keys()].map(id => document.getElementById(id)).filter(Boolean);
      const observer = new IntersectionObserver(entries => {
        const intersecting = entries.filter(entry => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (!intersecting.length) return;
        const id = intersecting[0].target.id;
        links.forEach(link => {
          const current = anchorMap.get(id) === link;
          if (current) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      }, { rootMargin: "-20% 0px -65% 0px", threshold: [0, .1, .25] });
      sections.forEach(section => observer.observe(section));
    }
  });
})();
