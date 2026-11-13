/* Noetfield cinematic orbital infrastructure scene. Original deterministic procedural artwork.
   Real visual composition, no generated business metrics. */
(()=>{'use strict';
const main=document.querySelector('[data-cc-scene]');if(!main)return;
const ctx=main.getContext('2d');if(!ctx)return;
const W=1060,H=480;
function rnd(s){return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}};
const rand=rnd(121113);
const towers=Array.from({length:155},(_,i)=>{const a=rand()*Math.PI*2,r=Math.sqrt(rand()),depth=Math.sin(a);return {x:530+Math.cos(a)*r*302,y:338+Math.sin(a)*r*73,h:13+rand()*106*(.75+.25*(1-r)),w:9+rand()*16,shade:rand(),depth,i}}).sort((a,b)=>a.y-b.y);
function rgba(hex,a){let n=parseInt(hex.slice(1),16);return 'rgba('+((n>>16)&255)+','+((n>>8)&255)+','+(n&255)+','+a+')'}
function ellipse(c,x,y,rx,ry,col,line=1,fill){c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);if(fill){c.fillStyle=fill;c.fill()}if(col){c.strokeStyle=col;c.lineWidth=line;c.stroke()}}
function line(c,x1,y1,x2,y2,color,width=1){c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.lineWidth=width;c.strokeStyle=color;c.stroke()}
function glow(c,x,y,r,color){const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,color);g.addColorStop(1,'transparent');c.fillStyle=g;c.fillRect(x-r,y-r,r*2,r*2)}
function tower(c,t){const {x,y,h,w}=t;const left=x-w*.55,top=y-h,depth=w*.32;
c.fillStyle='#111f40';c.beginPath();c.moveTo(left,top);c.lineTo(left+w,top);c.lineTo(left+w,y);c.lineTo(left,y);c.closePath();c.fill();
let g=c.createLinearGradient(left,0,left+w,0);g.addColorStop(0,'#6082ac');g.addColorStop(.2,'#2c416e');g.addColorStop(1,'#071329');c.fillStyle=g;c.fillRect(left,top,w,h);
c.fillStyle='#101b37';c.beginPath();c.moveTo(left+w,top);c.lineTo(left+w+depth,top-depth*.6);c.lineTo(left+w+depth,y-depth*.6);c.lineTo(left+w,y);c.closePath();c.fill();
c.fillStyle='#91a3cf';c.beginPath();c.moveTo(left,top);c.lineTo(left+depth,top-depth*.6);c.lineTo(left+w+depth,top-depth*.6);c.lineTo(left+w,top);c.closePath();c.fill();
c.strokeStyle='rgba(173,181,241,.48)';c.lineWidth=.5;c.strokeRect(left,top,w,h);
const rows=Math.floor(h/9),cols=Math.max(1,Math.floor(w/5));for(let j=0;j<rows;j++){for(let k=0;k<cols;k++){let seed=(t.i*13+j*7+k*19)%11;if(seed<7){c.fillStyle=seed<2?'rgba(248,191,115,.92)':'rgba(161,178,248,.55)';c.fillRect(left+3+k*5,top+5+j*9,1.8,2.6)}}}
if(t.shade>.71)glow(c,x,top,6,'rgba(255,201,121,.4)');
}
function draw(){const r=main.getBoundingClientRect();if(!r.width)return;let scale=Math.min(devicePixelRatio||1,2);main.width=Math.round(r.width*scale);main.height=Math.round(r.height*scale);ctx.setTransform(main.width/W,0,0,main.height/H,0,0);ctx.clearRect(0,0,W,H);
glow(ctx,545,214,290,'rgba(91,47,215,.27)');glow(ctx,535,390,320,'rgba(200,133,54,.13)');
const earth=ctx.createRadialGradient(600,590,100,555,585,700);earth.addColorStop(0,'rgba(32,51,115,.30)');earth.addColorStop(.59,'rgba(10,19,45,.21)');earth.addColorStop(1,'transparent');ctx.fillStyle=earth;ctx.fillRect(0,220,1060,260);
ellipse(ctx,540,460,650,124,'rgba(118,153,253,.42)',4);ellipse(ctx,540,455,680,140,'rgba(174,137,255,.21)',1);
ellipse(ctx,545,357,382,112,'rgba(102,90,177,.68)',12,'#081329');ellipse(ctx,545,351,377,101,'rgba(248,207,136,.67)',3);
ellipse(ctx,545,344,356,87,'rgba(98,109,196,.55)',7,'#09172f');ellipse(ctx,545,336,338,78,'rgba(246,200,125,.38)',2,'#142642');
for(let a=0;a<38;a++){let th=a*Math.PI*2/38;const x=545+350*Math.cos(th),y=340+78*Math.sin(th);line(ctx,545,340,x,y,'rgba(107,123,187,.08)',.6)}
towers.forEach(t=>tower(ctx,t));
ellipse(ctx,545,359,387,107,'rgba(250,193,118,.16)',22);ellipse(ctx,545,359,382,103,'rgba(255,207,129,.77)',3.6);
glow(ctx,541,358,126,'rgba(228,164,86,.16)');
/* intersecting gold orbitals and perspective rings */
ctx.save();ctx.translate(539,206);ctx.rotate(-.12);ellipse(ctx,0,0,332,75,'rgba(244,178,78,.2)',19);ellipse(ctx,0,0,333,74,'#eebd78',5);ellipse(ctx,0,0,298,57,'rgba(247,200,123,.68)',2);ctx.restore();
ctx.save();ctx.translate(540,206);ctx.rotate(.12);ellipse(ctx,0,0,265,95,'rgba(203,160,255,.36)',2);ctx.restore();
/* central crystalline execution tower */
glow(ctx,540,157,128,'rgba(151,66,255,.39)');
const grad=ctx.createLinearGradient(484,30,618,277);grad.addColorStop(0,'rgba(214,165,255,.25)');grad.addColorStop(.45,'rgba(92,58,231,.31)');grad.addColorStop(1,'rgba(107,47,217,.08)');
ctx.fillStyle=grad;ctx.strokeStyle='rgba(184,142,255,.94)';ctx.lineWidth=2.5;
ctx.beginPath();ctx.moveTo(537,20);ctx.lineTo(605,75);ctx.lineTo(609,238);ctx.lineTo(539,286);ctx.lineTo(474,239);ctx.lineTo(471,76);ctx.closePath();ctx.fill();ctx.stroke();
line(ctx,537,20,539,286,'rgba(218,184,255,.73)',1.5);line(ctx,471,76,539,116,'rgba(218,184,255,.55)',2);line(ctx,539,116,605,75,'rgba(218,184,255,.55)',2);
ctx.save();ctx.translate(540,166);ctx.font='800 116px Inter,Arial,sans-serif';ctx.textAlign='center';ctx.shadowBlur=30;ctx.shadowColor='#9b5aff';const ng=ctx.createLinearGradient(-65,-65,60,50);ng.addColorStop(0,'#f8f4ff');ng.addColorStop(.35,'#d1a4ff');ng.addColorStop(.7,'#8b69ff');ng.addColorStop(1,'#f0ddff');ctx.fillStyle=ng;ctx.fillText('N',0,0);ctx.restore();
glow(ctx,540,18,20,'rgba(252,243,225,.88)');glow(ctx,540,282,34,'rgba(189,102,255,.73)');
for(let i=0;i<35;i++){let a=i*2.399,rr=90+(i*31)%370,x=535+Math.cos(a)*rr,y=210+Math.sin(a)*rr*.4;glow(ctx,x,y,2+(i%3)*2,i%4?'rgba(242,189,117,.64)':'rgba(170,146,255,.85)')}
ellipse(ctx,545,390,405,112,'rgba(114,95,229,.35)',1);
}
let raf;const schedule=()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(draw)};
if('ResizeObserver'in window)new ResizeObserver(schedule).observe(main);else window.addEventListener('resize',schedule,{passive:true});
document.fonts?.ready?.then(schedule);schedule();
})();