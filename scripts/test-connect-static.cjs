const fs = require('node:fs');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const path = require('node:path');
const root=path.resolve(__dirname,'..');
const page=fs.readFileSync(path.join(root,'connect','index.html'),'utf8');
const contact=fs.readFileSync(path.join(root,'contact','index.html'),'utf8');
const opportunities=fs.readFileSync(path.join(root,'opportunities','index.html'),'utf8');
assert.match(page,/<title>Noetfield Connect/);
assert.match(page,/rel="canonical" href="https:\/\/www\.noetfield\.com\/connect\/"/);
assert.match(page,/href="#apply"/);
assert.match(page,/window\.NFIntakeCore/);
assert.match(page,/core\.postIntake\(/);
assert.match(page,/r\.intake_persisted===false/);
assert.match(page,/r\.intake_persisted!==true/);
assert.match(page,/form_id:"nfConnectWizard",topic:val\("intent"\)/);
assert.match(page,/var submissionId="RID-CNX-"/);
for (const field of ['intent','initiative','title','description','name','email','org','nextStep']) {
  assert.ok(page.includes('name="'+field+'"'), 'required field missing '+field);
}
for (const category of ['partnership','growth','capital','people','events','business','other']) {
  assert.ok(page.includes('value="'+category+'"'), 'missing type '+category);
}
for (const initiative of ['portfolio','noetfield','workforce','buildrelay','sourcea','trustfield','other','buildworkflow','outboundos','signalforge','earnloop','misenorth','interiormatch']) {
  assert.ok(page.includes('value="'+initiative+'"'), 'missing initiative '+initiative);
}
assert.match(page,/TrustField \/ independent venture/);
assert.doesNotMatch(page,/translateFa|hreflang="fa"|lang="fa"/);
assert.match(page,/var guidance=/);
assert.match(page,/consent_contact:form\.elements\.namedItem\("contactConsent"\)\.checked/);
assert.match(page,/No account or introductory meeting required/);
assert.match(page,/not an accepted agreement, guaranteed meeting/);
assert.match(contact,/href="\/connect\/">Partnerships/);
assert.match(opportunities,/href="\/connect\/">Start guided intake/);
const scripts=[...page.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,1,'expected one inline JS bundle');
for(const m of scripts) new vm.Script(m[1],{filename:'connect-inline.js'});

// The public progressive Connect bundle is corporate marketing, not a private desk.
// Check source as well as the exact Pages artifact language boundary on build.
const progressive=fs.readFileSync(path.join(root,'assets','noetfield-connect-v3.js'),'utf8');
assert.doesNotMatch(progressive,/[\u0600-\u06FF]/);
assert.doesNotMatch(progressive,/translateExtras|params\.get\("lang"\)|fa\?/);
for(const feature of ['participant/status','participant/feedback','nf-connect-saved','chooseFromLink']) {
 assert.ok(progressive.includes(feature),'regressed English progressive intake feature: '+feature);
}
new vm.Script(progressive,{filename:'noetfield-connect-v3.js'});

const desk=fs.readFileSync(path.join(root,'assets','opportunity-desk.html'),'utf8');
// Founder Desk is an authenticated operator tool and may be localized.
// The English-only rule applies to the corporate PUBLIC output, not this source.
assert.match(desk,/X-Desk-CSRF/);
assert.match(desk,/relationship-graph/);
assert.match(desk,/invitation-form/);
assert.ok(desk.includes('/api/opportunities/desk/page'));
assert.match(desk,/conversionVerified/);
for (const id of ['owner-filter','source-filter','type-filter','match-filter','collab-filter','conversion-filter']) {
  assert.ok(desk.includes('id="'+id+'"'),'missing operational filter '+id);
}
for (const view of ['all','unowned','due','matching','collaboration','conversion']) {
  assert.ok(desk.includes('data-view="'+view+'"'),'missing case view '+view);
}
assert.doesNotMatch(desk,/localStorage|sessionStorage|setInterval|X-Admin-Secret/);
assert.doesNotMatch(page,/[\u0600-\u06FF]/);
assert.doesNotMatch(opportunities,/[\u0600-\u06FF]/);
assert.match(page,/CONNECTION TO OUTCOME/);
assert.match(page,/id="routeGuidance"/);
assert.match(desk,/todayLocal/);

const deskScripts=[...desk.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(deskScripts.length,1,'expected one private operator JS bundle');
for (const m of deskScripts) new vm.Script(m[1],{filename:'connect-english-desk.js'});

console.log('PASS: Noetfield Connect structural and JavaScript syntax smoke checks');