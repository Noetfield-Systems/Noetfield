/* Corporate trust and conversion acceptance: public source, not synthetic traction. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const terms=read("terms/index.html");
const privacy=read("privacy/index.html");
const contact=read("contact/index.html");
const work=read("work-with-us/index.html");
const home=read("index.html");
const proof=read("proof/index.html");
const trust=read("trust/index.html");
const js=read("assets/noetfield-collaboration-entry.js");
const sitemap=read("sitemap.xml");
const applications=read("applications/index.html");
const investors=read("investors/index.html");
for(const [name,html] of [["terms",terms],["privacy",privacy],["contact",contact],["trust",trust],["home",home]]){
 assert.match(html,/<html lang="en">/,'English corporate page: '+name);
 assert.match(html,/href="\/connect\/(?:\?[^"]*)?"/,'Connect reachable: '+name);
 assert.doesNotMatch(html,/<nav aria-label="Products">\s*<strong>Products<\/strong>\s*<a href="\/applications\/trustfield\/">/,'TrustField cannot appear as corporate product: '+name);
}
assert.match(terms,/Terms of use/);
assert.match(terms,/Updated:<\/strong> 13 November 2026/);
assert.doesNotMatch(terms,/Copilot Governance Pack|Trust Brief \(\$10k\)|tle-receipt.yaml|Board PDF in your next governance meeting/);
assert.match(terms,/A request reference is not an accepted contract/);
assert.match(privacy,/Connect contributor and opportunity context/);
assert.match(privacy,/Case status and feedback/);
assert.match(privacy,/explicitly opts in/);
assert.match(privacy,/WorkforceOS/);
assert.match(contact,/type=people&amp;source=contact/);
assert.match(contact,/intent=business&amp;source=contact/);
assert.match(contact,/id="nfContactForm"/);
assert.match(work,/Start guided Connect intake/);
assert.match(work,/id="nfCorporateCollaborationForm"/);
assert.match(work,/there is no separate collaboration database/);
assert.match(js,/if\(!consent\|\|!consent.checked\)return/);
assert.match(home,/One execution layer. Clear company boundaries./);
assert.match(home,/TrustField is an <strong>independent venture<\/strong>/);
assert.doesNotMatch(home,/Four product surfaces/);
assert.match(home,/Reliability Case 001/);
assert.match(home,/claims-boundary-correction/);
assert.match(proof,/Three evidence-led case studies/);
assert.match(proof,/No claim of external customer adoption/);
assert.match(trust,/not an authenticated account/);
assert.doesNotMatch(applications,/TrustField product boundary/);
assert.doesNotMatch(investors,/TrustField product boundary/);
for(const p of ["","contact/","privacy/","terms/","proof/","work-with-us/"]){
 const loc="https://www.noetfield.com/"+p;
 const start=sitemap.indexOf("<loc>"+loc+"</loc>");
 assert.ok(start>=0,"missing sitemap "+loc);
 assert.match(sitemap.slice(start,start+155),/<lastmod>2026-11-13<\/lastmod>/,"stale lastmod "+loc);
}
console.log("PASS: corporate boundaries, real case studies, opt-in analytics, public contact and legal page coherence");
