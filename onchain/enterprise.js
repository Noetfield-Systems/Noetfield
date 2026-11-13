/* NOETFIELD OS / Enterprise solution routes. Progressive navigation only. */
(function(){
"use strict";
function boot(){
 const menu=document.getElementById("nfMenu"),header=document.querySelector(".nf-header"),nav=document.getElementById("nfNav");
 if(!menu||!header||!nav)return;
 const close=()=>{header.classList.remove("nf-open");menu.setAttribute("aria-expanded","false");menu.setAttribute("aria-label","Open service navigation");};
 menu.addEventListener("click",()=>{const open=menu.getAttribute("aria-expanded")!=="true";header.classList.toggle("nf-open",open);menu.setAttribute("aria-expanded",open?"true":"false");menu.setAttribute("aria-label",open?"Close service navigation":"Open service navigation");});
 nav.querySelectorAll("a").forEach(link=>link.addEventListener("click",close));
 document.addEventListener("keydown",e=>{if(e.key==="Escape")close();});
 document.addEventListener("click",e=>{if(!header.contains(e.target))close();});
 window.matchMedia("(min-width:1121px)").addEventListener("change",close);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})();