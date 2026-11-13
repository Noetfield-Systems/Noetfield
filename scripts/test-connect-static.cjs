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
assert.match(page,/href="\/connect\/\?lang=fa"/);
assert.match(page,/var isFa=/);
assert.match(page,/consent_contact:form\.elements\.namedItem\("contactConsent"\)\.checked/);
assert.match(page,/No account or introductory meeting required/);
assert.match(page,/not an accepted agreement, guaranteed meeting/);
assert.match(contact,/href="\/connect\/">Partnerships/);
assert.match(opportunities,/href="\/connect\/">Start guided intake/);
const scripts=[...page.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,1,'expected one inline JS bundle');
for(const m of scripts) new vm.Script(m[1],{filename:'connect-inline.js'});

const desk=fs.readFileSync(path.join(root,'assets','opportunity-desk.html'),'utf8');
assert.match(desk,/<html lang="fa" dir="rtl">/);
assert.match(desk,/X-Desk-CSRF/);
assert.match(desk,/relationship-graph/);
assert.match(desk,/invitation-form/);
assert.ok(desk.includes('/api/opportunities/desk/page'));
assert.match(desk,/verifiedConversion/);
for (const id of ['owner-filter','source-filter','type-filter','match-filter','collab-filter','conversion-filter']) {
  assert.ok(desk.includes('id="'+id+'"'),'missing operational filter '+id);
}
for (const view of ['all','unowned','due','matching','collaboration','conversion']) {
  assert.ok(desk.includes('data-view="'+view+'"'),'missing case view '+view);
}
assert.doesNotMatch(desk,/localStorage|sessionStorage|setInterval|X-Admin-Secret/);
const deskScripts=[...desk.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(deskScripts.length,1,'expected one private operator JS bundle');
for (const m of deskScripts) new vm.Script(m[1],{filename:'connect-persian-desk.js'});

console.log('PASS: Noetfield Connect structural and JavaScript syntax smoke checks');