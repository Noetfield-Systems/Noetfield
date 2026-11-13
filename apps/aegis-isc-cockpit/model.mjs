/** Noetfield AEGIS ISC — evidence-gated internal readiness model. Not an ISC evaluation. */
export const SOURCE='https://ised-isde.canada.ca/site/innovative-solutions-canada/en/artificial-intelligence-ai-decision-making-process-visibility-traceability-and-compliance-governance';
export const NOTICE='https://canadabuys.canada.ca/en/tender-opportunities/tender-notice/cb-189-51083224';
export const DEADLINE='2026-12-22T14:00:00-05:00';
export const CRITERIA=[
{id:'Q3b',title:'پیشرفت نسبت به فناوری روز',en:'Advance on state of the art',max:20,options:[0,5,12,20],need:'مقایسه اندازه‌گیری‌شده با روش دستی و فناوری‌های موجود؛ خط مبنا، داده خام، روش، بازبین مستقل',owner:'مسئول ارزیابی فنی',tag:'M-SOTA',priority:1},
{id:'Q1b',title:'چهار قابلیت تکمیلی',en:'Additional outcomes',max:10,options:[0,3,6,10],need:'استقرار محلی/کانادایی، مسیر EN/FR، جداسازی مستأجرها و هشدار/یکپارچه‌سازی',owner:'رهبر مهندسی',priority:4},
{id:'Q4',title:'ریسک‌های علمی و فنی',en:'Scientific and technical risks',max:10,options:[0,5,10],need:'ثبت ریسک‌های فنی با آزمون کاهش ریسک، خروجی، مسئول و احتمال/اثر',owner:'رهبر ML',priority:3},
{id:'Q5',title:'ریسک‌های اجرای پروژه',en:'Project risks',max:10,options:[0,5,10],need:'نیروی انسانی، بودجه، IP، تأمین، زمان‌بندی، اقدامات کاهش خطر',owner:'مدیر پروژه',priority:4},
{id:'Q6',title:'برنامه توسعه فاز ۲',en:'Project plan',max:20,options:[0,10,20],need:'برنامه ۱۸–۲۰ماهه، گیت پذیرش، TRL خروج، کارهای همزمان و وابستگی‌ها',owner:'Founder / مدیر پروژه',priority:3},
{id:'Q7',title:'تیم پیاده‌سازی',en:'Implementation team',max:20,options:[0,10,20],need:'افراد نام‌دار، مهارت و سوابق، تعهد و زمان حضور مستند و نقش واقعی',owner:'Founder',priority:2},
{id:'Q8',title:'مشارکت فراگیر',en:'Inclusivity',max:20,options:[0,10,20],need:'سیاست‌ها و اقدامات قابل اجرا؛ امتیاز ۲۰ فقط با ثبت معتبر در فهرست‌های مشخص بومی',owner:'مدیر پروژه',priority:7},
{id:'Q9',title:'کنترل و نظارت مالی',en:'Financial controls',max:10,options:[0,5,10],need:'مرکز هزینه، کنترل هزینه، ثبت زمان و صورتحساب، مسئول دارای صلاحیت و گزارش مالی',owner:'مسئول مالی',priority:5},
{id:'Q10',title:'تجاری‌سازی',en:'Commercialization',max:10,options:[0,5,10],need:'بخش مشتری، مصاحبه/پایلوت واقعی، قیمت‌گذاری، مسیر فروش و مستندات تمایل مشتری',owner:'Founder / رشد',priority:4}
];
export const GATES=[
{id:'ELIG',title:'واجد شرایط بودن شرکت',need:'اسناد ثبتی، نسبت FTE، محل R&D، دستمزدها، مدیران و شرکت‌های وابسته',priority:1},
{id:'E1',title:'تغییر سیاست و ارزیابی مجدد',need:'گراف نسخه‌بندی، تعیین سیستم‌های متأثر، گزارش قبل/بعد',priority:2},
{id:'E2',title:'یکپارچگی API و سیستم‌ها',need:'OpenAPI، تبادل عملی با دست‌کم ۳ سطح، داده خام و قراردادها',priority:3},
{id:'E3',title:'دسترسی و چرخه‌عمر داده',need:'آزمون منفی RBAC، محل داده، نگهداری، خروجی و حذف خودخدمت',priority:3},
{id:'E4',title:'پنج چارچوب و پنج وضعیت',need:'نگاشت ۵ منبع کانادایی، traceability، پنج وضعیت و ارجاع به شواهد',priority:1},
{id:'E5',title:'بازبینی انسانی و رویداد ممیزی',need:'تغییر/رد/تأیید یافته توسط بازبین مجاز با تاریخچه ثبت‌شده',priority:3},
{id:'E6',title:'ارزیابی بومی داده/مدل/خروجی',need:'اجراکننده نخست‌طرفِ سنجه‌های داده، مدل و خروجی AI با آزمایش تکرارپذیر',priority:1},
{id:'M-TRL',title:'Q2 — TRL 5 تا ۹',need:'آزمون یکپارچه واقعی در محیط شبیه‌سازی‌شده با روش، نتایج، تاریخ و نام آزمونگر',priority:1},
{id:'M-INNOV',title:'Q3a — نوآوری غیرتدریجی',need:'تعریف نوآوری، اثبات فنی و تمایز قابل سنجش نسبت به وضع موجود',priority:1},
{id:'M-SOTA',title:'Q3b — برتری قابل دفاع',need:'بنچمارک مستقیم و نتیجه قابل استناد که حداقل ۵ امتیاز را توجیه کند',priority:1}
];
export const PILOT=[
{id:'M1',phase:'هفته ۱',start:1,end:5,title:'صلاحیت، ممیزی و فهرست شواهد',owner:'Founder + مالی',gate:'ELIG',exit:'اسناد صلاحیت و inventory دارای URL و SHA و محدودیت'},
{id:'M2',phase:'هفته ۱–۲',start:4,end:11,title:'کامپایلر سیاست و ارزیاب بومی',owner:'مهندسی + متخصص ML',gate:'E6',exit:'اجرای واقعی native data/model/output با raw fixtures'},
{id:'M3',phase:'هفته ۲',start:8,end:16,title:'Replay تاریخی و پنج چارچوب',owner:'Founder + Policy SME',gate:'E4',exit:'داده before/after، ۵ وضعیت، ارجاع نسخه و بازبین'},
{id:'M4',phase:'هفته ۲–۳',start:12,end:21,title:'اتصال، جداسازی مستأجر و lifecycle',owner:'مهندس + امنیت',gate:'E3',exit:'۳ قرارداد API، تست منفی، export/delete و EN/FR'},
{id:'M5',phase:'هفته ۳–۴',start:17,end:25,title:'مطالعه کنترل‌شده و آزمون رقبا',owner:'بازبین مستقل',gate:'M-SOTA',exit:'labels، baseline، CI، نتایج واقعی، عدم ادعای برتری بدون داده'},
{id:'M6',phase:'هفته ۴',start:23,end:30,title:'تیم، مشتری، پیش‌داوری و پرونده',owner:'Founder + مالی',gate:'M-TRL',exit:'تعهدنامه‌ها، مصاحبه/پایلوت، بودجه، mock review و readiness verdict'}
];
const addDays=(start,n)=>{const d=new Date(start+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10)};
const task=(id,title,tag,owner,day,priority=2,kind='evidence')=>({id,title,tag,owner,kind,due:addDays('2026-11-12',day),priority,status:'open',blocker:'',nextAction:'گردآوری سند واقعی و ثبت مرجع و بازبین',notes:''});
export function seed(){return {
 schema:1,project:'Noetfield AEGIS',solicitation:'EN578-24ISC4/100',pilotStart:'2026-11-12',
 ratings:Object.fromEntries(CRITERIA.map(c=>[c.id,0])),gateReviews:Object.fromEntries(GATES.map(g=>[g.id,'unreviewed'])),
 evidence:[],people:[],activities:[],risks:[],commercial:[],
 tasks:[
 task('T1','راستی‌آزمایی صلاحیت و نسبت‌های کانادایی','ELIG','Founder + حسابدار',3,1),
 task('T2','نسخه و SHA مدارک واقعی کد و اجرا','E1','Founder + مهندس',5,1),
 task('T3','اجرای native metrics روی داده، مدل و خروجی','E6','رهبر ML',10,1),
 task('T4','پنج چارچوب با ارجاع نسخه و پنج وضعیت','E4','Policy SME',13,1),
 task('T5','بازاجرا و گزارش diff تاریخی','E1','Founder',15,1),
 task('T6','سه اتصال عملی + آزمون‌های tenant','E2','مهندس + امنیت',20,1),
 task('T7','TRL5 dossier: روش، نتایج، تستر','M-TRL','Founder + بازبین',23,1),
 task('T8','مقایسه عملی با روش دستی و ابزارهای موجود','M-SOTA','بازبین مستقل',24,1),
 task('T9','تعهد حضور و مهارت افراد ضروری','Q7','Founder',25,2),
 task('T10','سه مصاحبه مشتری و یک trial محدوده‌دار','Q10','رشد / Founder',25,2,'interview'),
 task('T11','ریسک‌های فنی و پروژه + طرح مهار','Q4','رهبر مهندسی',18,2),
 task('T12','بودجه، کنترل مالی و خروجی TRL فاز ۲','Q9','Founder + مالی',27,2),
 task('T13','پیش‌داوری مستقل پرونده و رفع gap','Q3b','بازبین مستقل',29,1)
 ],
 milestones:PILOT.map(m=>({...m,id:m.id,due:addDays('2026-11-12',m.end-1),status:'open',owner:m.owner,linkedEvidence:[]})),
 referenceEvidence:[
 {title:'Policy snapshots',url:'https://github.com/Noetfield-Systems/NOETFIELD-RUNWAY/blob/main/docs/policy-language.md',observation:'کد سیاست — صرفاً مرجع اولیه؛ هنوز اثبات نگاشت تعهدات AI نیست',classification:'source-inspected'},
 {title:'Adapter protocol',url:'https://github.com/Noetfield-Systems/NOETFIELD-RUNWAY/blob/main/packages/app-v2-runtime/src/adapter-protocol.ts',observation:'پروتکل آداپتور — اثبات سه ادغام مستقل نیست',classification:'source-inspected'},
 {title:'Receipt verifier',url:'https://github.com/Noetfield-Systems/NOETFIELD-RUNWAY/blob/main/apps/project-runtime-control-plane/src/runway-receipt-verify.ts',observation:'راستی‌آزمایی receipt — آزمون بومی کیفیت AI نیست',classification:'source-inspected'}
 ],
 history:[{at:'2026-11-12T00:00:00Z',score:0,reason:'راه‌اندازی رجیستری؛ هیچ شواهدی به‌عنوان قبول‌شده وارد نشده است'}],audit:[]
};}
export const isReviewed=e=>e&&e.kind!=='hypothetical'&&e.status==='reviewed'&&/^https:\/\//.test(e.url||'')&&!!(e.reviewer||'').trim()&&!!e.reviewedAt&&!!e.observedAt&&!!(e.claim||'').trim()&&!!(e.limitations||'').trim();
export function evaluate(s){
 const reviewed=(s.evidence||[]).filter(isReviewed),tags=new Set(reviewed.flatMap(e=>Array.isArray(e.tags)?e.tags:[]));
 const scores={}; for(const c of CRITERIA){
   const requested=Number((s.ratings||{})[c.id]||0),choice=c.options.includes(requested)?requested:0;
   let value=reviewed.some(e=>(e.criteria||[]).includes(c.id))?choice:0;
   if(c.id==='Q1b'){
    const n=['A1','A2','A3','A4'].filter(x=>tags.has(x)).length;
    value=Math.min(value,n===4?10:n>=2?6:n===1?3:0);
   }
   if(c.id==='Q3b'&&!reviewed.some(e=>e.type==='benchmark'&&e.tags?.includes('M-SOTA')))value=0;
   if(c.id==='Q8'&&value===20&&!reviewed.some(e=>e.type==='indigenous-directory'&&e.criteria?.includes('Q8'))) value=10;
   if(c.id==='Q7'&&value){const committed=(s.people||[]).filter(p=>p.availability==='signed'&&p.proofUrl?.startsWith('https://'));if(!committed.length)value=0; else if(committed.length<3)value=Math.min(value,10);}
   scores[c.id]=value;
 }
 const gateStatuses={}; for(const g of GATES){
  const hasEvidence=tags.has(g.id);
  const review=(s.gateReviews||{})[g.id];
  gateStatuses[g.id]=review==='passed'&&hasEvidence?'passed':review==='failed'?'failed':hasEvidence?'needs-review':'missing';
 }
 if(scores.Q3b<5)gateStatuses['M-SOTA']='missing';
 const total=Object.values(scores).reduce((a,b)=>a+b,0);
 const openGates=GATES.filter(g=>gateStatuses[g.id]!=='passed');
 const required=CRITERIA.filter(c=>scores[c.id]<c.max).sort((a,b)=>a.priority-b.priority);
 const gaps=[...openGates.map(g=>({id:g.id,type:'gate',title:g.title,need:g.need,priority:g.priority,status:gateStatuses[g.id]})),...required.map(c=>({id:c.id,type:'criterion',title:c.title,need:c.need,priority:c.priority,status:scores[c.id]===0?'missing':'partial'}))].sort((a,b)=>a.priority-b.priority);
 const allGatesPass=openGates.length===0;
 const verdict=total>=65&&allGatesPass?'ready-for-internal-review':total>=65?'score-only-not-ready':'not-ready';
 const pointsTo65=Math.max(0,65-total);
 const milestoneGates=(s.milestones||[]).map(m=>{const reviewedProof=reviewed.filter(e=>(m.linkedEvidence||[]).includes(e.id));return {...m,canClose:reviewedProof.length>0&&gateStatuses[m.gate]==='passed',proofCount:reviewedProof.length}});
 const followups=(s.activities||[]).filter(a=>a.nextAction&&a.nextDate&&a.status!=='blocked').map(a=>({id:a.id,title:'پیگیری: '+a.title,owner:a.owner||'مسئول تعیین نشده',due:a.nextDate,nextAction:a.nextAction,status:'open',priority:2,kind:a.type}));
 const next=[...(s.tasks||[]).filter(t=>t.status!=='done'),...followups].sort((a,b)=>(a.status==='blocked'?1:0)-(b.status==='blocked'?1:0)||String(a.due).localeCompare(String(b.due))||a.priority-b.priority).slice(0,6);
 return {score:total,max:130,threshold:65,pointsTo65,scores,gateStatuses,openGates,gaps,verdict,reviewedEvidenceCount:reviewed.length,totalEvidence:(s.evidence||[]).length,verifiedTags:[...tags],milestones:milestoneGates,next,scenarios:[{name:'Weak / not ready',score:43,type:'hypothetical'},{name:'Evidence-built',score:102,type:'hypothetical'},{name:'Strong hypothetical',score:120,type:'hypothetical'}]};
}
export function normalizeEntity(collection,value){
 const str=v=>String(v??'').trim().slice(0,2400);
 const common={...value,id:str(value.id)||crypto.randomUUID(),updatedAt:new Date().toISOString()};
 if(collection==='evidence'){
  if(!str(common.title)||!/^https:\/\//i.test(str(common.url)))throw Error('عنوان و لینک HTTPS برای سند الزامی‌اند.');
  if(common.kind==='hypothetical')throw Error('مدرک فرضی را نمی‌توان در رجیستری شواهد واقعی ثبت کرد.');
  common.tags=Array.isArray(common.tags)?common.tags.filter(x=>[...GATES.map(g=>g.id),'A1','A2','A3','A4'].includes(x)):[];
  common.criteria=Array.isArray(common.criteria)?common.criteria.filter(x=>CRITERIA.some(c=>c.id===x)):[];
  if(common.status==='reviewed'){
   if(!common.reviewer||!common.observedAt||!common.claim||!common.limitations)throw Error('برای بازبینی سند، بازبین، تاریخ مشاهده، ادعا و محدودیت را ثبت کنید.');
   common.reviewedAt=common.reviewedAt||new Date().toISOString();
  }else{common.status=['collected','rejected'].includes(common.status)?common.status:'collected';common.reviewedAt=null;}
 } else if(collection==='tasks'){
  if(!str(common.title)||!str(common.owner)||!/^\d{4}-\d{2}-\d{2}$/.test(str(common.due)))throw Error('عنوان، مسئول و تاریخ YYYY-MM-DD لازم است.');
  common.status=['open','progress','blocked','done'].includes(common.status)?common.status:'open';
 } else if(collection==='milestones'){
  if(common.status==='done'&&!(common.linkedEvidence||[]).length)throw Error('برای بستن milestone حداقل یک سند مرتبط لازم است.');
 }else if(['people','activities','risks','commercial'].includes(collection)){
  if(!str(common.title||common.name))throw Error('عنوان یا نام لازم است.');
 }else throw Error('نوع داده نامعتبر است.');
 return common;
}