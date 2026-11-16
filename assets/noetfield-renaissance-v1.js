/* Noetfield Renaissance: progressive enhancement only.
   Reuses current CRM intake, does not create fictitious signups or transactions. */
(function(){
  "use strict";
  const q=(s,r=document)=>r.querySelector(s);
  const qa=(s,r=document)=>Array.from(r.querySelectorAll(s));
  const menu=q("[data-nr-menu]");
  const nav=q("[data-nr-nav]");
  if(menu&&nav){
    menu.addEventListener("click",()=>{
      const open=menu.getAttribute("aria-expanded")==="true";
      menu.setAttribute("aria-expanded",String(!open));
      nav.dataset.open=String(!open);
    });
    nav.addEventListener("click",e=>{
      if(e.target.closest("a")){menu.setAttribute("aria-expanded","false");nav.dataset.open="false";}
    });
    document.addEventListener("keydown",e=>{
      if(e.key==="Escape"){menu.setAttribute("aria-expanded","false");nav.dataset.open="false";}
    });
  }
  qa("[data-nr-filter]").forEach(button=>{
    button.addEventListener("click",()=>{
      const kind=button.dataset.nrFilter;
      qa("[data-nr-filter]").forEach(b=>b.setAttribute("aria-pressed",String(b===button)));
      qa("[data-nr-category]").forEach(card=>{
        const tags=(card.dataset.nrCategory||"").split(/\s+/);
        card.dataset.hidden=String(kind!=="all"&&!tags.includes(kind));
      });
    });
  });
  const volume=q("#nr-workflow-volume");
  const mins=q("#nr-workflow-minutes");
  const rate=q("#nr-workflow-rate");
  const weekly=q("#nr-workflow-week");
  const yearly=q("#nr-workflow-year");
  const estimate=q("#nr-workflow-value");
  function updateCalc(){
    if(!volume||!mins||!weekly||!yearly)return;
    const v=Math.min(10000,Math.max(0,Number(volume.value)||0));
    const m=Math.min(240,Math.max(0,Number(mins.value)||0));
    const h=v*m/60;
    weekly.textContent=h.toLocaleString("en-CA",{maximumFractionDigits:1});
    yearly.textContent=(h*52).toLocaleString("en-CA",{maximumFractionDigits:0});
    if(estimate){const r=Math.max(0,Number(rate?.value)||0);estimate.textContent=(h*52*r).toLocaleString("en-CA",{maximumFractionDigits:0,style:"currency",currency:"CAD"});}
  }
  [volume,mins,rate].filter(Boolean).forEach(x=>x.addEventListener("input",updateCalc));
  updateCalc();
  qa("[data-nr-share]").forEach(button=>{
    button.addEventListener("click",async()=>{
      const address="https://www.noetfield.com/community/";
      if(navigator.clipboard?.writeText){
        try{await navigator.clipboard.writeText(address);button.textContent="Link copied";return;}catch(_){}
      }
      button.textContent="Copy: noetfield.com/community/";
    });
  });
  qa("[data-nr-proposal]").forEach(a=>{
    a.addEventListener("click",()=>{
      const select=q("#nfOpportunityTopic");
      const topic=a.dataset.nrProposal||"strategic-partnership";
      if(select){
        if(Array.from(select.options).some(o=>o.value===topic))select.value=topic;
      }
      const note=q('#nfOpportunityForm textarea[name="notes"]');
      if(note&&!note.value.trim()&&a.dataset.nrPrompt){
        note.placeholder=a.dataset.nrPrompt;
      }
    });
  });
  // If a provider analytics integration is already installed, emit intent-only events.
  // A click is not a lead, purchase, booked meeting, or delivered project.
  qa("[data-nr-event]").forEach(el=>{
    el.addEventListener("click",()=>{
      if(Array.isArray(window.dataLayer)){
        window.dataLayer.push({event:"nr_intent_click",intent:el.dataset.nrEvent,path:location.pathname});
      }
    });
  });
})();
