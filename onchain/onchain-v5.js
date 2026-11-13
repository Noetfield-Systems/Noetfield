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
/* V6 interaction system: controlled client UI only; no wallet, XP or financial state manufactured. */
(function () {
  "use strict";
  function onReady(fn) { if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn, {once:true}); else fn(); }
  onReady(function() {
    var menu = document.getElementById("onchainMenuToggle");
    var nav = document.getElementById("onchainNav");
    var header = menu && menu.closest(".v5-header");
    if (menu && nav && header) {
      function closeMenu() { header.classList.remove("v6-menu-open"); menu.setAttribute("aria-expanded","false"); menu.setAttribute("aria-label","Open navigation"); }
      menu.addEventListener("click", function() {
        var open = menu.getAttribute("aria-expanded") !== "true";
        header.classList.toggle("v6-menu-open",open);
        menu.setAttribute("aria-expanded",open?"true":"false");
        menu.setAttribute("aria-label",open?"Close navigation":"Open navigation");
      });
      nav.querySelectorAll("a").forEach(function(link){link.addEventListener("click",closeMenu);});
      document.addEventListener("keydown",function(event){if(event.key==="Escape")closeMenu();});
      document.addEventListener("click",function(event){if(!header.contains(event.target))closeMenu();});
      window.matchMedia("(min-width: 1051px)").addEventListener("change",closeMenu);
    }
    var layerInfo = {
      asset:{title:"Business & Asset Layer",copy:"Start with an actual asset, enforceable rights, accountable entities and the data required to execute a commercial workflow.",href:"https://scan.noetfield.com/rwa-clinic/",label:"Inspect RWA readiness demo ↗"},
      policy:{title:"Policy & Control Layer",copy:"Convert rules into auditable decisions: authority checks, eligibility gates, confirmation requirements and controlled rejection.",href:"https://control.noetfield.com/sandbox",label:"Explore authorization sandbox ↗"},
      execution:{title:"Execution & Integration",copy:"Scope the smallest working integration: existing apps, APIs, wallet providers, agents and contracts with acceptance tests.",href:"#project",label:"Scope your implementation ↗"},
      verification:{title:"Verification & Operations",copy:"Confirm outcomes using receipts, reconciliation records and independently checkable evidence instead of assumed success.",href:"https://www.noetfield.com/proof/",label:"View verification examples ↗"}
    };
    var layerButtons = [].slice.call(document.querySelectorAll("[data-layer]"));
    var title = document.getElementById("v6LayerTitle"), copy = document.getElementById("v6LayerCopy"), link = document.getElementById("v6LayerLink");
    layerButtons.forEach(function(button){
      button.addEventListener("click",function(){
        var info = layerInfo[button.dataset.layer]; if (!info) return;
        layerButtons.forEach(function(b){var current=b===button;b.classList.toggle("is-active",current);b.setAttribute("aria-pressed",current?"true":"false");});
        if(title) title.textContent=info.title;
        if(copy) copy.textContent=info.copy;
        if(link){link.textContent=info.label;link.href=info.href;if(info.href.indexOf("https:")===0){link.target="_blank";link.rel="noopener noreferrer";}else{link.removeAttribute("target");link.removeAttribute("rel");}}
      });
    });
    var networks={
      ethereum:{title:"Ethereum",copy:"Exploring EVM-compatible contract and policy-controlled execution architecture."},
      solana:{title:"Solana",copy:"Evaluating high-throughput network primitives and suitable integration requirements."},
      polygon:{title:"Polygon",copy:"Assessing EVM scaling environments for business workflows and verifiable receipts."},
      base:{title:"Base",copy:"Exploring the Base EVM environment for cost-aware operational applications and policy-controlled transactions."},
      bnb:{title:"BNB Chain",copy:"Evaluating BNB Smart Chain integration patterns; no production partnership or launch is implied."},
      icp:{title:"Internet Computer",copy:"Studying onchain application and hosting patterns for programmable workflows."},
      berachain:{title:"Berachain",copy:"Monitoring EVM ecosystem design and potential technical interoperability."}
    };
    var buttons = [].slice.call(document.querySelectorAll("[data-network]"));
    var detail = document.getElementById("v6NetworkDetail");
    var networkTitle = document.getElementById("v6NetworkName"), networkCopy = document.getElementById("v6NetworkCopy");
    buttons.forEach(function(button){button.addEventListener("click",function(){
      var selected = networks[button.dataset.network]; if(!selected)return;
      buttons.forEach(function(b){b.setAttribute("aria-pressed",b===button?"true":"false");});
      if(networkTitle)networkTitle.textContent=selected.title;
      if(networkCopy)networkCopy.textContent=selected.copy;
      if(detail)detail.classList.add("v6-detail-shown");
    });});
  });
})();
