#!/usr/bin/env node
import fs from "node:fs";
const middleware=fs.readFileSync("functions/_middleware.js","utf8");
const config=JSON.parse(fs.readFileSync("data/nf-www-onchain-proxy-v1.json","utf8"));
const start=middleware.indexOf("const GOV_PROXY = ")+ "const GOV_PROXY = ".length;
const end=middleware.indexOf(";\n",start);
const proxy=JSON.parse(middleware.slice(start,end));
if(!proxy.enabled)throw Error("Onchain proxy not enabled");
for(const path of config.paths){
 if(proxy.origins[path]!==config.origin)throw Error("Missing or mismatched route "+path);
}
const untouched=[
 "/onchain/rwa/","/onchain/hub/","/onchain/policy/","/onchain/stablecoin/",
 "/onchain/agents/","/onchain/whitepaper/","/onchain/hero-architecture-hd.webp",
 "/api/intake","/api/stripe/webhook","/about/","/status/"
];
function match(path){
 const prefixes=Object.keys(proxy.origins).sort((a,b)=>b.length-a.length);
 return prefixes.find(p=>path===p||path.startsWith(p+"/"))||null;
}
for(const path of untouched){
 if(match(path)?.startsWith("/onchain")||match(path)?.startsWith("/api/architect")||match(path)?.startsWith("/api/public")||match(path)==="/api/providers/apply")throw Error("Legacy route hijacked: "+path);
}
for(const path of ["/onchain/","/onchain/architect/","/onchain/network/","/onchain/economy/","/onchain/proof/","/onchain/app.js","/onchain/styles.css","/api/architect/intents","/api/public/network","/api/providers/apply"]){
 if(!match(path))throw Error("New app route not proxied: "+path);
}
console.log("PASS Onchain-OS path forwarding:",config.paths.length,"approved routes, legacy Pages routes untouched");
