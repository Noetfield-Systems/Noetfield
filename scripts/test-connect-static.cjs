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
assert.match(page,/No account or introductory meeting required/);
assert.match(page,/not an accepted agreement, guaranteed meeting/);
assert.match(contact,/href="\/connect\/">Partnerships/);
assert.match(opportunities,/href="\/connect\/">Start guided intake/);
const scripts=[...page.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,1,'expected one inline JS bundle');
for(const m of scripts) new vm.Script(m[1],{filename:'connect-inline.js'});
console.log('PASS: Noetfield Connect structural and JavaScript syntax smoke checks');