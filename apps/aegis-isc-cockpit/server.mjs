import http from 'node:http';
import {readFile,mkdir,writeFile,rename} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHmac,randomUUID,timingSafeEqual} from 'node:crypto';
import {seed,evaluate,CRITERIA,GATES,SOURCE,NOTICE,DEADLINE,normalizeEntity,isReviewed} from './model.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));
const dataDir=process.env.DATA_DIR||path.join(root,'data');
const storeFile=path.join(dataDir,'aegis-isc.json');
const admin=process.env.ADMIN_PASSWORD;
const key=process.env.SESSION_SECRET;
if(!admin||admin.length<12||!key||key.length<32){console.error('ADMIN_PASSWORD (>=12 chars) and SESSION_SECRET (>=32 chars) required.');process.exit(1)}
const port=Number(process.env.PORT||3000);
let state;let mutex=Promise.resolve();const attempts=new Map();
await mkdir(dataDir,{recursive:true,mode:0o700});
try {state=JSON.parse(await readFile(storeFile,'utf8'));if(!state||state.schema!==1)throw Error('Unknown store schema');}catch(e){if(e.code!=='ENOENT')throw e;state=seed();await safeSave(state)}
async function safeSave(s){const f=storeFile+'.'+randomUUID()+'.tmp';await writeFile(f,JSON.stringify(s,null,2),{mode:0o600});await rename(f,storeFile)}
function eq(a,b){const x=Buffer.from(String(a||'')),y=Buffer.from(String(b||''));return x.length===y.length&&timingSafeEqual(x,y)}
function sign(exp){return createHmac('sha256',key).update(exp).digest('hex')}
function loginCookie(req){const exp=String(Date.now()+12*3600*1000);return `aegis_session=${exp}.${sign(exp)}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200${secure(req)?'; Secure':''}`}
function secure(req){return req.headers['x-forwarded-proto']==='https'||Boolean(req.socket.encrypted)}
function authorized(req){const raw=(req.headers.cookie||'').split('; ').find(x=>x.startsWith('aegis_session='))?.split('=')[1];if(!raw)return false;const [exp,sig]=raw.split('.');return /^\d{13}$/.test(exp||'')&&Number(exp)>Date.now()&&eq(sign(exp),sig)}
function respond(res,status,payload,extra={}){const text=JSON.stringify(payload);res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',...extra});res.end(text)}
async function body(req){let total=0,raw='';for await(const chunk of req){total+=chunk.length;if(total>160_000)throw Error('حجم درخواست بیش از حد است.');raw+=chunk.toString('utf8')}let x;try{x=JSON.parse(raw||'{}')}catch{throw Error('JSON نامعتبر است.')}if(!x||typeof x!=='object'||Array.isArray(x))throw Error('بدنه نامعتبر است.');return x}
function originOkay(req){const o=req.headers.origin;if(!o)return true;try{return new URL(o).host===req.headers.host}catch{return false}}
async function mutate(op,actor='operator'){
 const job=mutex.then(async()=>{const s=structuredClone(state);const before=evaluate(s).score;const info=await op(s);const after=evaluate(s).score;const at=new Date().toISOString();
 s.audit=[...(s.audit||[]),{id:randomUUID(),at,actor,action:info?.action||'update',target:info?.target||'',previousScore:before,nextScore:after}].slice(-1200);
 s.history=[...(s.history||[]),{at,score:after,reason:info?.action||'ویرایش'}].slice(-1000);
 await safeSave(s);state=s;return {state:s,derived:evaluate(s),...info};});
 mutex=job.then(()=>{},()=>{});return job;
}
const files={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css'};
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8'};
const server=http.createServer(async(req,res)=>{
 res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('X-Frame-Options','DENY');res.setHeader('Cache-Control','no-store');
 res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; connect-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'");
 if(secure(req))res.setHeader('Strict-Transport-Security','max-age=31536000; includeSubDomains');
 const url=new URL(req.url,'http://localhost');
 try{
  if(url.pathname==='/api/health'){return respond(res,200,{ok:true,app:'aegis-isc',version:'1.0.0',persistence:'file'})}
  if(url.pathname==='/api/auth/login'&&req.method==='POST'){
   if(!originOkay(req))return respond(res,403,{error:'Origin نامعتبر است.'});
   const ip=(req.socket.remoteAddress||'unknown');const a=attempts.get(ip)||{count:0,until:0};if(a.count>=8&&a.until>Date.now())return respond(res,429,{error:'تلاش بیش از حد. بعداً دوباره تلاش کنید.'});
   const p=await body(req);if(!eq(p.password,admin)){attempts.set(ip,{count:a.count+1,until:Date.now()+15*60_000});return respond(res,401,{error:'رمز ورود اشتباه است.'})}
   attempts.delete(ip);return respond(res,200,{ok:true},{'Set-Cookie':loginCookie(req)});
  }
  if(url.pathname==='/api/auth/logout'&&req.method==='POST')return respond(res,200,{ok:true},{'Set-Cookie':'aegis_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'});
  if(url.pathname.startsWith('/api/')){
   if(!authorized(req))return respond(res,401,{error:'ورود به فضای خصوصی لازم است.'});
   if(req.method!=='GET'&&!originOkay(req))return respond(res,403,{error:'Origin نامعتبر است.'});
   if(url.pathname==='/api/state'&&req.method==='GET')return respond(res,200,{state,derived:evaluate(state),meta:{criteria:CRITERIA,gates:GATES,source:SOURCE,notice:NOTICE,deadline:DEADLINE}});
   if(url.pathname==='/api/export'&&req.method==='GET'){
    const t=url.searchParams.get('format');if(t==='csv'){
     const csvCell=x=>'"'+String(x??'').replaceAll('"','""')+'"';const cols=['id','title','type','status','url','reviewer','observedAt','criteria','tags','claim','limitations'];
     const csv='\uFEFF'+[cols.join(','),...(state.evidence||[]).map(e=>cols.map(k=>csvCell(Array.isArray(e[k])?e[k].join('|'):e[k])).join(','))].join('\r\n');
     res.writeHead(200,{'Content-Type':'text/csv; charset=utf-8','Content-Disposition':'attachment; filename="aegis-isc-evidence.csv"'});return res.end(csv);
    }
    res.writeHead(200,{'Content-Type':'application/json; charset=utf-8','Content-Disposition':'attachment; filename="aegis-isc-evidence-pack.json"'});return res.end(JSON.stringify({exportedAt:new Date().toISOString(),source:SOURCE,state,derived:evaluate(state)},null,2));
   }
   if(url.pathname==='/api/rating'&&req.method==='POST'){
    const p=await body(req);const c=CRITERIA.find(x=>x.id===p.id);if(!c||!c.options.includes(Number(p.value)))return respond(res,400,{error:'امتیاز خارج از جدول رسمی است.'});
    const r=await mutate(s=>{s.ratings[p.id]=Number(p.value);return {action:'assess-criterion',target:p.id}});return respond(res,200,{state:r.state,derived:r.derived});
   }
   if(url.pathname==='/api/gate'&&req.method==='POST'){
    const p=await body(req);if(!GATES.some(x=>x.id===p.id)||!['unreviewed','passed','failed'].includes(p.value))return respond(res,400,{error:'وضعیت گیت نامعتبر است.'});
    if(p.value==='passed'&&!state.evidence.some(e=>isReviewed(e)&&e.tags?.includes(p.id)))return respond(res,400,{error:'برای PASS ابتدا سند واقعی بازبینی‌شده و مرتبط با این گیت ثبت کنید.'});
    const r=await mutate(s=>{s.gateReviews[p.id]=p.value;return {action:'review-gate',target:p.id}});return respond(res,200,{state:r.state,derived:r.derived});
   }
   if(url.pathname==='/api/record'&&req.method==='POST'){
    const p=await body(req),coll=String(p.collection||'');if(!['evidence','tasks','milestones','people','activities','risks','commercial'].includes(coll))return respond(res,400,{error:'مجموعه نامعتبر است.'});
    const r=await mutate(s=>{const value=normalizeEntity(coll,p.record||{});const i=s[coll].findIndex(x=>x.id===value.id);
     if(coll==='milestones'&&value.status==='done'){
      const model=evaluate(s),proof=(value.linkedEvidence||[]).filter(id=>s.evidence.some(e=>e.id===id&&isReviewed(e)));
      if(!proof.length||model.gateStatuses[value.gate]!=='passed')throw Error('گیت خروج milestone هنوز PASS نشده یا سند بازبینی‌شده ندارد.');
     }
     if(i>=0)s[coll][i]=value;else s[coll].unshift(value);return {action:i>=0?'update-'+coll:'create-'+coll,target:value.id};});
    return respond(res,200,{state:r.state,derived:r.derived});
   }
   if(url.pathname==='/api/delete'&&req.method==='POST'){
    const p=await body(req),coll=String(p.collection||'');if(!['evidence','tasks','people','activities','risks','commercial'].includes(coll))return respond(res,400,{error:'حذف این مجموعه مجاز نیست.'});
    const r=await mutate(s=>{s[coll]=s[coll].filter(x=>x.id!==p.id);return {action:'delete-'+coll,target:p.id}});return respond(res,200,{state:r.state,derived:r.derived});
   }
   return respond(res,404,{error:'API یافت نشد.'});
  }
  if(req.method!=='GET'||!files[url.pathname]){res.writeHead(404);return res.end('Not found')}
  const name=files[url.pathname];const data=await readFile(path.join(root,'public',name));res.writeHead(200,{'Content-Type':types[path.extname(name)]});res.end(data);
 }catch(e){console.error('request failed',e.message);respond(res,/نامعتبر|لازم|الزامی|مجاز|سند|گیت|تاریخ|حجم|خارج|مسئول|عنوان/.test(e.message)?400:500,{error:/نامعتبر|لازم|الزامی|مجاز|سند|گیت|تاریخ|حجم|خارج|مسئول|عنوان/.test(e.message)?e.message:'خطای غیرمنتظره سرور'})}
});
server.listen(port,'0.0.0.0',()=>console.log(`AEGIS ISC listening on :${port}`));