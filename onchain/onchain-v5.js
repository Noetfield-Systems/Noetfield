/* Noetfield Onchain: front-end scoped project guide and existing assistant entry.
   Does not issue tokens, grant airdrops, accept funds or replace server-side intake. */
(function(){
  "use strict";
  var cases={
    "rwa-private-credit":{
      title:"Map asset rights and policy requirements",
      description:"Start with the issuer, commercial rights, investor eligibility and required operating integrations. A technical scope can then be defined.",
      topic:"rwa-private-credit",
      template:"I am evaluating an RWA / private-credit workflow. Please help scope rights mapping, issuer operations, eligibility requirements and the integration architecture."
    },
    "stablecoin-operations":{
      title:"Map business payments and reconciliation",
      description:"Define the current invoice and approval flow, payment provider requirements and traceable financial reconciliation.",
      topic:"stablecoin-operations",
      template:"I need a stablecoin-enabled business operations integration using suitable providers. Please scope approval controls, payment requests, reconciliation and reporting."
    },
    "agent-authorization":{
      title:"Define authority and controlled execution",
      description:"Specify which agent actions are allowed, which need confirmation and how decisions and receipts are independently verified.",
      topic:"agent-authorization",
      template:"I want an AI agent operating workflow with clearly bounded authority, policy checks, confirmation gates and independent verification."
    },
    "onchain-engineering":{
      title:"Scope the missing application layer",
      description:"Identify the product API, smart-contract, wallet or backend integration and define acceptance tests around one working outcome.",
      topic:"onchain-engineering",
      template:"I need a Web3 product engineering sprint with a defined API, smart contract or wallet integration, technical acceptance tests and a delivery plan."
    }
  };
  function ready(fn){if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",fn,{once:true});}else{fn();}}
  ready(function(){
    var active="rwa-private-credit";
    var options=[].slice.call(document.querySelectorAll("[data-scope-route]"));
    var heading=document.getElementById("v5ScopeHeading");
    var detail=document.getElementById("v5ScopeDescription");
    options.forEach(function(button){
      button.addEventListener("click",function(){
        var key=button.getAttribute("data-scope-route");
        if(!Object.prototype.hasOwnProperty.call(cases,key))return;
        active=key;
        options.forEach(function(b){var selected=b===button;b.classList.toggle("is-active",selected);b.setAttribute("aria-pressed",selected?"true":"false");});
        if(heading)heading.textContent=cases[key].title;
        if(detail)detail.textContent=cases[key].description;
      });
      button.setAttribute("aria-pressed",button.getAttribute("data-scope-route")===active?"true":"false");
    });
    var prepare=document.getElementById("v5PrepareScope");
    if(prepare)prepare.addEventListener("click",function(){
      var form=document.getElementById("nfOnchainIntake");
      if(!form)return;
      var topic=form.querySelector('[name="topic"]');
      var notes=form.querySelector('[name="notes"]');
      var cfg=cases[active];
      if(topic)topic.value=cfg.topic;
      if(notes&&!notes.value.trim())notes.value=cfg.template;
      form.scrollIntoView({behavior:window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});
      var email=form.querySelector('[name="email"]');
      if(email)window.setTimeout(function(){email.focus({preventScroll:true});},350);
    });
    var openAgent=document.getElementById("v5OpenAgent");
    if(openAgent)openAgent.addEventListener("click",function(){
      var chat=document.querySelector(".nfChatFab, #nfChatFab, [aria-label='Open Noetfield assistant']");
      if(chat){chat.click();return;}
      document.getElementById("v5PrepareScope")?.focus();
      if(detail)detail.textContent="The live assistant is unavailable in this browser. You can still prepare an enquiry with the guided scope tool and existing intake form.";
    });
    /* No fake waitlist counts or local-only confirmations; success is rendered only by NFIntakeCore. */
  });
})();